from bson import ObjectId

from pillar.tests import AbstractPillarTest
from pillar.tests import common_test_data as ctd


class PurgeHomeProjectsTest(AbstractPillarTest):
    def test_purge(self):
        self.create_standard_groups()
        # user_a will be soft-deleted, user_b will be hard-deleted.
        # We don't support soft-deleting users yet, but the code should be
        # handling that properly anyway.
        user_a = self.create_user(user_id=24 * 'a', roles={'subscriber'}, token='token-a')
        user_b = self.create_user(user_id=24 * 'b', roles={'subscriber'}, token='token-b')

        # GET the home project to create it.
        home_a = self.get('/api/bcloud/home-project', auth_token='token-a').json()
        home_b = self.get('/api/bcloud/home-project', auth_token='token-b').json()

        with self.app.app_context():
            users_coll = self.app.db('users')

            res = users_coll.update_one({'_id': user_a}, {'$set': {'_deleted': True}})
            self.assertEqual(1, res.modified_count)

            res = users_coll.delete_one({'_id': user_b})
            self.assertEqual(1, res.deleted_count)

        from pillar.cli.maintenance import purge_home_projects

        with self.app.app_context():
            self.assertEqual(2, purge_home_projects(go=True))

            proj_coll = self.app.db('projects')
            self.assertEqual(True, proj_coll.find_one({'_id': ObjectId(home_a['_id'])})['_deleted'])
            self.assertEqual(True, proj_coll.find_one({'_id': ObjectId(home_b['_id'])})['_deleted'])


class UpgradeAttachmentUsageTest(AbstractPillarTest):
    def setUp(self, **kwargs):
        super().setUp(**kwargs)
        self.pid, self.uid = self.create_project_with_admin(user_id=24 * 'a')

        with self.app.app_context():
            files_coll = self.app.db('files')

            res = files_coll.insert_one({
                **ctd.EXAMPLE_FILE,
                'project': self.pid,
                'user': self.uid,
            })
            self.fid = res.inserted_id

    def test_image_link(self):
        with self.app.app_context():
            nodes_coll = self.app.db('nodes')
            res = nodes_coll.insert_one({
                **ctd.EXAMPLE_NODE,
                'picture': self.fid,
                'project': self.pid,
                'user': self.uid,
                'description': "# Title\n\n@[slug0]\n@[slug1]\n@[slug2]\nEitje van Fabergé.",
                'properties': {
                    'status': 'published',
                    'content_type': 'image',
                    'file': self.fid,
                    'attachments': {
                        'slug0': {
                            'oid': self.fid,
                            'link': 'self',
                        },
                        'slug1': {
                            'oid': self.fid,
                            'link': 'custom',
                            'link_custom': 'https://cloud.blender.org/',
                        },
                        'slug2': {
                            'oid': self.fid,
                        },
                    }
                }
            })
            nid = res.inserted_id

        from pillar.cli.maintenance import upgrade_attachment_usage

        with self.app.app_context():
            upgrade_attachment_usage(proj_url=ctd.EXAMPLE_PROJECT['url'], go=True)
            node = nodes_coll.find_one({'_id': nid})

            self.assertEqual(
                "# Title\n\n"
                "{attachment 'slug0' link='self'}\n"
                "{attachment 'slug1' link='https://cloud.blender.org/'}\n"
                "{attachment 'slug2'}\n"
                "Eitje van Fabergé.",
                node['description'],
                'The description should be updated')
            self.assertEqual(
                "<h1>Title</h1>\n"
                "<!-- {attachment 'slug0' link='self'} -->\n"
                "<!-- {attachment 'slug1' link='https://cloud.blender.org/'} -->\n"
                "<!-- {attachment 'slug2'} -->\n"
                "<p>Eitje van Fabergé.</p>\n",
                node['_description_html'],
                'The _description_html should be updated')

            self.assertEqual(
                {'slug0': {'oid': self.fid},
                 'slug1': {'oid': self.fid},
                 'slug2': {'oid': self.fid},
                 },
                node['properties']['attachments'],
                'The link should have been removed from the attachment')

    def test_post(self):
        """This requires checking the dynamic schema of the node."""
        with self.app.app_context():
            nodes_coll = self.app.db('nodes')
            res = nodes_coll.insert_one({
                **ctd.EXAMPLE_NODE,
                'node_type': 'post',
                'project': self.pid,
                'user': self.uid,
                'picture': self.fid,
                'description': "meh",
                'properties': {
                    'status': 'published',
                    'content': "# Title\n\n@[slug0]\n@[slug1]\n@[slug2]\nEitje van Fabergé.",
                    'attachments': {
                        'slug0': {
                            'oid': self.fid,
                            'link': 'self',
                        },
                        'slug1': {
                            'oid': self.fid,
                            'link': 'custom',
                            'link_custom': 'https://cloud.blender.org/',
                        },
                        'slug2': {
                            'oid': self.fid,
                        },
                    }
                }
            })
            nid = res.inserted_id

        from pillar.cli.maintenance import upgrade_attachment_usage

        with self.app.app_context():
            upgrade_attachment_usage(proj_url=ctd.EXAMPLE_PROJECT['url'], go=True)
            node = nodes_coll.find_one({'_id': nid})

            self.assertEqual(
                "# Title\n\n"
                "{attachment 'slug0' link='self'}\n"
                "{attachment 'slug1' link='https://cloud.blender.org/'}\n"
                "{attachment 'slug2'}\n"
                "Eitje van Fabergé.",
                node['properties']['content'],
                'The content should be updated')
            self.assertEqual(
                "<h1>Title</h1>\n"
                "<!-- {attachment 'slug0' link='self'} -->\n"
                "<!-- {attachment 'slug1' link='https://cloud.blender.org/'} -->\n"
                "<!-- {attachment 'slug2'} -->\n"
                "<p>Eitje van Fabergé.</p>\n",
                node['properties']['_content_html'],
                'The _content_html should be updated')

            self.assertEqual(
                {'slug0': {'oid': self.fid},
                 'slug1': {'oid': self.fid},
                 'slug2': {'oid': self.fid},
                 },
                node['properties']['attachments'],
                'The link should have been removed from the attachment')
