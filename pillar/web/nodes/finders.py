"""Node-URL-finding microframework."""

import logging

from flask import current_app, url_for
import werkzeug.exceptions as wz_exceptions

import pillarsdk
from pillarsdk import Node
from pillarsdk.exceptions import ResourceNotFound

from pillar.web.utils import caching
from pillar.web import system_util

log = logging.getLogger(__name__)

node_url_finders = {}  # mapping from node type to callable.


def register_node_finder(node_type):
    """Decorator, registers the decorated function as node finder for the given node type."""

    def wrapper(func):
        if node_type in node_url_finders:
            raise ValueError('Node type %r already handled by %r' %
                             (node_type, node_url_finders[node_type]))

        log.debug('Registering %s node finder for node type %r',
                  func, node_type)
        node_url_finders[node_type] = func
        return func

    return wrapper


@register_node_finder('comment')
def find_for_comment(project, node):
    """Returns the URL for a comment."""

    api = system_util.pillar_api()

    parent = node
    while parent.node_type == 'comment':
        if isinstance(parent.parent, pillarsdk.Resource):
            parent = parent.parent
            continue

        try:
            parent = Node.find(parent.parent, api=api)
        except ResourceNotFound:
            log.warning(
                'url_for_node(node_id=%r): Unable to find parent node %r',
                node['_id'], parent.parent)
            raise ValueError('Unable to find parent node %r' % parent.parent)

    # Find the redirection URL for the parent node.
    parent_url = find_url_for_node(parent)
    if '#' in parent_url:
        # We can't attach yet another fragment, so just don't link to
        # the comment for now.
        return parent_url
    return parent_url + '#{}'.format(node['_id'])


@register_node_finder('post')
def find_for_post(project, node):
    """Returns the URL for a blog post."""

    project_id = project['_id']
    if str(project_id) == current_app.config['MAIN_PROJECT_ID']:
        return url_for('main.main_blog',
                       url=node.properties.url)

    the_project = project_url(project_id, project=project)
    return url_for('main.project_blog',
                   project_url=the_project.url,
                   url=node.properties.url)


def find_for_other(project, node):
    """Fallback: Assets, textures, and other node types.

    Hard-coded fallback, so doesn't need @register_node_finder() decoration.
    """

    if not project:
        raise ValueError(f'project={project}')

    the_project = project_url(project['_id'], project=project)

    return url_for('projects.view_node',
                   project_url=the_project.url,
                   node_id=node['_id'])


@caching.cache_for_request()
def project_url(project_id, project):
    """Returns the project, raising a ValueError if it can't be found.

    Uses the "urler" service endpoint.
    """

    if project is not None:
        return project

    if not current_app.config['URLER_SERVICE_AUTH_TOKEN']:
        log.error('No URLER_SERVICE_AUTH_TOKEN token, unable to use URLer service.')
        return None

    urler_api = system_util.pillar_api(
        token=current_app.config['URLER_SERVICE_AUTH_TOKEN'])

    try:
        return pillarsdk.Project.find_from_endpoint(
            '/service/urler/%s' % project_id, api=urler_api)
    except pillarsdk.ForbiddenAccess as ex:
        log.error('URLER request to find URL for project %s failed: %s', project_id, ex)
        raise wz_exceptions.NotFound()


# Cache the actual URL based on the node ID, for the duration of the request.
@caching.cache_for_request()
def find_url_for_node(node):
    # Find the node's project, or its ID, depending on whether a project
    # was embedded. This is needed some finder functions.
    if isinstance(node.project, pillarsdk.Resource):
        # Embedded project
        project = node.project
    else:
        project = project_url(node.project, None)
        if not project:
            raise ValueError(f'Project {node.project} not found')

    # Determine which function to use to find the correct URL.
    finder = node_url_finders.get(node.node_type, find_for_other)
    return finder(project, node)
