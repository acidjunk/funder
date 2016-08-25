import doctest
import json

from django.contrib.auth.models import User
from django.test import TestCase

from wagtail.wagtailcore.models import Page

from .models import (BlogPage, BlogTag, BlogPageTag, BlogIndexPage,
                     BlogCategory, BlogCategoryBlogPage)

from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group


class BlogTests(TestCase):
    def setUp(self):
        home = Page.objects.get(slug='home')
        self.user = User.objects.create_user('test', 'test@test.test', 'pass')
        self.xml_path = "example_export.xml"
        self.blog_index = home.add_child(instance=BlogIndexPage(
            title='Blog Index', slug='blog', search_description="x",
            owner=self.user))

    def test_index(self):
        url = self.blog_index.url
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        blog_page = self.blog_index.add_child(instance=BlogPage(
            title='Blog Page', slug='blog_page1', search_description="x",
            owner=self.user))
        url = blog_page.url
        res = self.client.get(url)
        self.assertContains(res, "Blog Page")

    def test_author(self):
        # make super to access admin
        self.user.is_superuser = True
        self.user.save()
        self.assertTrue(self.client.login(username='test', password='pass'))
        # make an is_staff admin
        staff_user = User.objects.create_user('mr.staff', 'staff@test.test', 'pass')
        staff_user.is_staff = True
        staff_user.save()
        # make some groups
        bloggers = 'Bloggers'
        Group.objects.create(name=bloggers)
        others = 'Others'
        Group.objects.create(name=others)
        # make a non-admin Blogger author
        author_user = User.objects.create_user('mr.author', 'author@test.test', 'pass')
        author_user.groups.add(Group.objects.get(name=bloggers))
        author_user.save()
        # make a blog page
        blog_page = self.blog_index.add_child(instance=BlogPage(
            title='Blog Page', slug='blog_page1', search_description="x",
            owner=self.user))

        with self.settings(BLOG_LIMIT_AUTHOR_CHOICES_GROUP=None, BLOG_LIMIT_AUTHOR_CHOICES_ADMIN=False):
            response = self.client.get(
                reverse('wagtailadmin_pages:edit', args=(blog_page.id, )),
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'mr.staff')
            self.assertNotContains(response, 'mr.author')

        with self.settings(BLOG_LIMIT_AUTHOR_CHOICES_GROUP=bloggers, BLOG_LIMIT_AUTHOR_CHOICES_ADMIN=False):
            response = self.client.get(
                reverse('wagtailadmin_pages:edit', args=(blog_page.id, )),
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'mr.staff')
            self.assertContains(response, 'mr.author')

        with self.settings(BLOG_LIMIT_AUTHOR_CHOICES_GROUP=bloggers, BLOG_LIMIT_AUTHOR_CHOICES_ADMIN=True):
            response = self.client.get(
                reverse('wagtailadmin_pages:edit', args=(blog_page.id, )),
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'mr.staff')
            self.assertContains(response, 'mr.author')

        with self.settings(BLOG_LIMIT_AUTHOR_CHOICES_GROUP=[bloggers, others], BLOG_LIMIT_AUTHOR_CHOICES_ADMIN=False):
            response = self.client.get(
                reverse('wagtailadmin_pages:edit', args=(blog_page.id, )),
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'mr.staff')
            self.assertContains(response, 'mr.author')

        with self.settings(BLOG_LIMIT_AUTHOR_CHOICES_GROUP=[bloggers, others], BLOG_LIMIT_AUTHOR_CHOICES_ADMIN=True):
            response = self.client.get(
                reverse('wagtailadmin_pages:edit', args=(blog_page.id, )),
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'mr.staff')
            self.assertContains(response, 'mr.author')

    def test_latest_entries_feed(self):
        self.blog_index.add_child(instance=BlogPage(
                                  title='Blog Page',
                                  slug='blog_page1',
                                  search_description="x",
                                  owner=self.user))
        res = self.client.get("{0}{1}/rss/".format(self.blog_index.url,
                                                   self.blog_index.slug))
        self.assertContains(res, "Blog Page")
        self.assertContains(res, '<rss')
        self.assertContains(res, 'version="2.0"')
        self.assertContains(res, '</rss>')

    def test_latest_entries_feed_atom(self):
        self.blog_index.add_child(instance=BlogPage(
                                  title='Blog Page',
                                  slug='blog_page1',
                                  search_description="x",
                                  owner=self.user))
        res = self.client.get("{0}{1}/atom/".format(self.blog_index.url,
                                                    self.blog_index.slug))
        self.assertContains(res, "Blog Page")
        self.assertContains(res, '<feed')
        self.assertContains(res, 'xmlns="http://'
                                 'www.w3.org/2005/Atom"')
        self.assertContains(res, '</feed>')
