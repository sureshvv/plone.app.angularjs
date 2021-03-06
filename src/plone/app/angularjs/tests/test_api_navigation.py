# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.angularjs.testing import\
    PLONE_APP_ANGULARJS_INTEGRATION_TESTING
from plone.app.angularjs.testing import\
    PLONE_APP_ANGULARJS_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from zope.interface import directlyProvides

from plone.app.angularjs.interfaces import IAPIRequest

import json
import unittest2 as unittest


class TestAngularJsTopNavigation(unittest.TestCase):

    layer = PLONE_APP_ANGULARJS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        directlyProvides(self.portal, IAPIRequest)

    def test_empty_navigation(self):
        view = getMultiAdapter(
            (self.portal, self.request),
            name="top_navigation"
        )
        self.assertEqual(json.loads(view()), [])

    def test_folder_in_navigation(self):
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.folder1.reindexObject()

        view = getMultiAdapter(
            (self.portal, self.request),
            name="top_navigation"
        )

        self.assertTrue(view())
        self.assertEqual(
            json.loads(view()),
            [{
                u'id': u'folder1',
                u'title': u'Folder 1',
                u'description': u'',
                u'path': 'folder1',
            }]
        )

    def test_document_not_in_navigation(self):
        self.portal.invokeFactory('Document', 'doc1', title='Document 1')

        view = getMultiAdapter(
            (self.portal, self.request),
            name="top_navigation"
        )

        self.assertEqual(
            json.loads(view()),
            []
        )

    def test_do_not_show_excluded_from_nav_documents(self):
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.folder1.exclude_from_nav = True
        self.portal.folder1.reindexObject(idxs=['exclude_from_nav'])

        view = getMultiAdapter(
            (self.portal, self.request),
            name="top_navigation"
        )

        self.assertEqual(
            len(json.loads(view())),
            0
        )


class TestAngularJsPortletNavigation(unittest.TestCase):

    layer = PLONE_APP_ANGULARJS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        directlyProvides(self.portal, IAPIRequest)

    def test_empty_navigation(self):
        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            json.loads(view()),
            []
        )

    def test_folder_in_navigation(self):
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            json.loads(view()),
            [{
                u'id': u'folder1',
                u'title': u'Folder 1',
                u'description': u'',
                u'path': u'folder1',
                u'children': []
            }]
        )

    def test_multiple_folders_in_navigation(self):
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.invokeFactory('Folder', 'folder2', title='Folder 2')

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            len(json.loads(view())), 2
        )
        self.assertEqual(
            [
                x['id'] for x
                in json.loads(view())
            ],
            ['folder1', 'folder2']
        )

    def test_do_not_show_excluded_from_nav_folder(self):
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.folder1.exclude_from_nav = True
        self.portal.folder1.reindexObject(idxs=['exclude_from_nav'])

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            len(json.loads(view())),
            0
        )

    def test_show_top_level_siblings_in_navigation(self):
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.invokeFactory('Folder', 'folder2', title='Folder 2')
        self.portal.invokeFactory('Folder', 'folder3', title='Folder 3')

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            len(json.loads(view())),
            3
        )
        self.assertEqual(
            [
                x['id'] for x
                in json.loads(view())
            ],
            ['folder1', 'folder2', 'folder3']
        )

    def test_show_top_level_siblings_in_navigation_with_nested(self):
        self.request.set('path', '/folder1')
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.invokeFactory('Folder', 'folder2', title='Folder 2')
        self.portal.invokeFactory('Folder', 'folder3', title='Folder 3')

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            len(json.loads(view())),
            3
        )

    def test_show_nested_folder_in_navigation(self):
        self.request.set('path', '/folder1/folder2')
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.folder1.invokeFactory(
            'Folder', 'folder2', title='Folder 2'
        )

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            json.loads(view())[0]['id'],
            'folder1'
        )
        self.assertEqual(
            json.loads(view())[0]['children'][0]['id'],
            'folder2'
        )
        self.assertEqual(
            json.loads(view())[0]['children'][0]['path'],
            'folder1/folder2'
        )

    def test_show_double_nested_folder_in_navigation(self):
        self.request.set('path', '/folder1/folder2/folder3')
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.folder1.invokeFactory(
            'Folder', 'folder2', title='Folder 2'
        )
        self.portal.folder1.folder2.invokeFactory(
            'Folder', 'folder3', title='Folder 3'
        )

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            json.loads(view())[0]['id'],
            'folder1'
        )

        self.assertEqual(
            json.loads(view())[0]['children'][0]['id'],
            'folder2'
        )
        self.assertEqual(
            json.loads(view())[0]['children'][0]['children'][0]['id'],
            'folder3'
        )

    def test_show_nested_folder_in_navigation_and_top_level_items(self):
        # root
        # +- folder1
        # +- folder2
        # |  + folder2-1
        # +- folder3
        self.request.set('path', '/folder2/folder2-1')
        self.portal.invokeFactory('Folder', 'folder1', title='Folder 1')
        self.portal.invokeFactory('Folder', 'folder2', title='Folder 2')
        self.portal.invokeFactory('Folder', 'folder3', title='Folder 3')
        self.portal.folder2.invokeFactory(
            'Folder', 'folder2-1', title='Folder 2-1'
        )

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            json.loads(view())[0]['id'],
            'folder1'
        )
        self.assertEqual(
            json.loads(view())[1]['id'],
            'folder2'
        )
        self.assertEqual(
            json.loads(view())[1]['children'][0]['id'],
            'folder2-1'
        )
        self.assertEqual(
            json.loads(view())[2]['id'],
            'folder3'
        )

    def test_show_three_nested_folder_in_navigation(self):
        # root
        # +- folder1
        # |  +- folder11
        # |     +- folder111
        self.request.set('path', '/folder1/folder11/folder111')
        self.portal.invokeFactory(
            'Folder', 'folder1', title='Folder 1')
        self.portal.folder1.invokeFactory(
            'Folder', 'folder11', title='Folder 11')
        self.portal.folder1.folder11.invokeFactory(
            'Folder', 'folder111', title='Folder 111')

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        first_child_id = json.loads(view())[0]['id']
        self.assertEqual(
            first_child_id,
            'folder1',
            'First child in the tree should be folder1.'
        )

        second_child_id = json.loads(view())[0]['children'][0]['id']
        self.assertEqual(
            second_child_id,
            'folder11',
            'Second child in the tree should be folder11.'
        )

        third_child_id = json.loads(
            view()
        )[0]['children'][0]['children'][0]['id']
        self.assertEqual(
            third_child_id,
            'folder111',
            'Third child in the tree should be folder111.'
        )

    def test_full(self):
        # root
        # +- front-page
        # +- news
        # |  + news1
        # +- events
        self.request.set('path', '/news')
        self.portal.invokeFactory('Folder', 'front-page', title='Front Page')
        self.portal.invokeFactory('Folder', 'news', title='News')
        self.portal.invokeFactory('Folder', 'events', title='Events')
        self.portal.news.invokeFactory(
            'Folder', 'news1', title='News 1'
        )

        view = getMultiAdapter(
            (self.portal, self.request),
            name="portlet_navigation"
        )

        self.assertEqual(
            json.loads(view())[0]['id'],
            'front-page'
        )
        self.assertEqual(
            json.loads(view())[1]['id'],
            'news'
        )
        self.assertEqual(
            json.loads(view())[1]['children'][0]['id'],
            'news1'
        )
        self.assertEqual(
            json.loads(view())[2]['id'],
            'events'
        )


class TestAngularJsPortletNavigationFunctional(unittest.TestCase):

    layer = PLONE_APP_ANGULARJS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        from plone.testing.z2 import Browser
        from plone.app.testing import SITE_OWNER_NAME
        from plone.app.testing import SITE_OWNER_PASSWORD
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_api_navigation_nested(self):
        self.portal.invokeFactory('Folder', 'news', title='News')
        self.portal.news.invokeFactory('Folder', 'news1', title='News 1')
        import transaction
        transaction.commit()
        self.browser.open(
            self.portal_url + '/++api++v1/portlet_navigation?path=/news/news1')
        output = json.loads(self.browser.contents)
        self.assertEqual(output[0]['id'], u'news')
        self.assertEqual(output[0]['children'][0]['id'], u'news1')
