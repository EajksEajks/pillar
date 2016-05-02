import itertools

import pymongo
from flask import Blueprint, current_app

from application.utils import jsonify

blueprint = Blueprint('latest', __name__)


def keep_fetching(collection, db_filter, projection, sort, py_filter, batch_size=12):
    """Yields results for which py_filter returns True"""

    curs = collection.find(db_filter, projection).sort(sort)
    curs.batch_size(batch_size)

    for doc in curs:
        if py_filter(doc):
            yield doc


def latest_nodes(db_filter, projection, py_filter, limit):
    nodes = current_app.data.driver.db['nodes']

    latest = keep_fetching(nodes, db_filter, projection,
                           [('_updated', pymongo.DESCENDING)],
                           py_filter, limit)

    result = list(itertools.islice(latest, limit))
    return result


def has_public_project(node_doc):
    """Returns True iff the project the node belongs to is public."""

    project_id = node_doc.get('project')
    return is_project_public(project_id)


# TODO: cache result, at least for a limited amt. of time, or for this HTTP request.
def is_project_public(project_id):
    """Returns True iff the project is public."""

    project = current_app.data.driver.db['projects'].find_one(project_id)
    if not project:
        return False

    return not project.get('is_private')


@blueprint.route('/assets')
def latest_assets():
    latest = latest_nodes({'node_type': 'asset', 'properties.status': 'published'},
                          {'name': 1, 'project': 1, 'user': 1, 'node_type': 1,
                           'picture': 1, 'properties.status': 1,
                           'properties.content_type': 1,
                           'permissions.world': 1},
                          has_public_project, 12)
    return jsonify({'_items': latest})


@blueprint.route('/comments')
def latest_comments():
    latest = latest_nodes({'node_type': 'comment', 'properties.status': 'published'},
                          {'project': 1, 'parent': 1, 'user': 1,
                           'properties.content': 1, 'node_type': 1, 'properties.status': 1,
                           'properties.is_reply': 1},
                          has_public_project, 6)

    # Embed the comments' parents.
    nodes = current_app.data.driver.db['nodes']
    parents = {}
    for comment in latest:
        parent_id = comment['parent']

        if parent_id in parents:
            comment['parent'] = parents[parent_id]
            continue

        parent = nodes.find_one(parent_id)
        parents[parent_id] = parent
        comment['parent'] = parent

    return jsonify({'_items': latest})


def setup_app(app, url_prefix):
    app.register_blueprint(blueprint, url_prefix=url_prefix)
