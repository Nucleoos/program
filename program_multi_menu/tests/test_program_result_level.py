# -*- coding: utf-8 -*-

###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.tests.common import TransactionCase
from openerp.osv.orm import except_orm


class test_program_result_level(TransactionCase):

    def setUp(self):
        super(test_program_result_level, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.program_result_level_model = self.registry("program.result.level")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)

        self.result_level_1_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Level 1',
                'top_level_menu': True,
                'top_level_menu_name': 'Test Menu Name',
            }, context=self.context)
        self.result_level_2_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Level 2',
                'parent_id': self.result_level_1_id,
            }, context=self.context)
        self.result_level_3_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Level 3',
                'parent_id': self.result_level_2_id,
            }, context=self.context)
        self.result_level_1 = self.program_result_level_model.browse(
            self.cr, self.uid, self.result_level_1_id, context=self.context
        )
        self.result_level_2 = self.program_result_level_model.browse(
            self.cr, self.uid, self.result_level_2_id, context=self.context
        )
        self.result_level_3 = self.program_result_level_model.browse(
            self.cr, self.uid, self.result_level_3_id, context=self.context
        )

    def test_root_menu_add(self):
        """Test Adding top menu configuration to a root level
        """
        self.assertTrue(self.result_level_3.write({
            'parent_id': False,
            'top_level_menu': True,
            'top_level_menu_name': 'Custom Level 3 Menu Name',
        }))

    def test_non_root_menu_add(self):
        """Test Adding top menu configuration to non root level
        """
        self.assertRaises(except_orm, self.result_level_3.write, {
            'top_level_menu': True,
            'top_level_menu_name': 'Custom Level 3 Menu Name',
        })

    def test_reverse(self):
        """Test bubbling up of Top Menu Configuration
        """

        self.result_level_3.write({'parent_id': False})
        self.result_level_2.write({'parent_id': self.result_level_3.id})
        self.result_level_1.write({'parent_id': self.result_level_2.id})

        self.result_level_3.refresh()
        self.result_level_2.refresh()
        self.result_level_1.refresh()

        self.assertFalse(self.result_level_1.top_level_menu)
        self.assertFalse(self.result_level_1.top_level_menu_name)
        self.assertFalse(self.result_level_2.top_level_menu)
        self.assertFalse(self.result_level_2.top_level_menu_name)
        self.assertTrue(self.result_level_3.top_level_menu)
        self.assertEqual(self.result_level_3.top_level_menu_name,
                         'Test Menu Name')

    def test_reverse_new_name(self):
        """Test bubbling up of Top Menu Configuration with name change
        """
        self.result_level_3.write({
            'parent_id': False,
            'top_level_menu': True,
            'top_level_menu_name': 'Custom Level 3 Menu Name',
        })
        self.result_level_3.refresh()
        self.result_level_2.write({'parent_id': self.result_level_3_id})
        self.result_level_2.refresh()
        self.result_level_1.write({'parent_id': self.result_level_2_id})
        self.result_level_1.refresh()
        self.assertTrue(self.result_level_3.top_level_menu)
        self.assertEqual(self.result_level_3.top_level_menu_name,
                         'Custom Level 3 Menu Name')

    def test_create_new_root(self):
        new_root_level_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'New Root',
                'child_id': [(6, 0, [self.result_level_1.id])],
            }, context=self.context)
        new_root_level = self.program_result_level_model.browse(
            self.cr, self.uid, new_root_level_id, context=self.context
        )
        self.assertTrue(new_root_level.top_level_menu)
        self.assertEqual(new_root_level.top_level_menu_name, 'Test Menu Name')

    def test_create_new_tail(self):
        """Testing creating a non-root level with menu information"""
        self.assertRaises(
            except_orm,
            self.program_result_level_model.create,
            self.cr, self.uid, {
                'name': 'New Tail',
                'parent_id': self.result_level_3_id,
                'top_level_menu': True,
                'top_level_menu_name': 'Custom New Tail Menu Name',
            }, context=self.context
        )