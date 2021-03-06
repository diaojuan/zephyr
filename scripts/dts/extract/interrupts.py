#
# Copyright (c) 2018 Bobby Noelte
#
# SPDX-License-Identifier: Apache-2.0
#

from extract.globals import *
from extract.directive import DTDirective

##
# @brief Manage interrupts directives.
#
class DTInterrupts(DTDirective):

    def __init__(self):
        pass

    def _find_parent_irq_node(self, node_path):
        address = ''

        for comp in node_path.split('/')[1:]:
            address += '/' + comp
            if 'interrupt-parent' in reduced[address]['props']:
                interrupt_parent = reduced[address]['props'][
                    'interrupt-parent']

        return phandles[interrupt_parent]

    ##
    # @brief Extract interrupts
    #
    # @param node_path Path to node owning the
    #                  interrupts definition.
    # @param prop compatible property name
    # @param names (unused)
    # @param def_label Define label string of node owning the
    #                  compatible definition.
    #
    def extract(self, node_path, prop, names, def_label):
        node = reduced[node_path]

        try:
            props = list(node['props'].get(prop))
        except:
            props = [node['props'].get(prop)]

        irq_parent = self._find_parent_irq_node(node_path)

        l_base = def_label.split('/')
        index = 0

        while props:
            prop_def = {}
            prop_alias = {}
            l_idx = [str(index)]

            try:
                name = [str_to_label(names.pop(0))]
            except:
                name = []

            cell_yaml = get_binding(irq_parent)
            l_cell_prefix = ['IRQ']

            for i in range(reduced[irq_parent]['props']['#interrupt-cells']):
                l_cell_name = [cell_yaml['#cells'][i].upper()]
                if l_cell_name == l_cell_prefix:
                    l_cell_name = []

                l_fqn = '_'.join(l_base + l_cell_prefix + l_idx + l_cell_name)
                prop_def[l_fqn] = props.pop(0)
                add_compat_alias(node_path,
                        '_'.join(l_cell_prefix + l_idx + l_cell_name),
                        l_fqn, prop_alias)

                if len(name):
                    alias_list = l_base + l_cell_prefix + name + l_cell_name
                    prop_alias['_'.join(alias_list)] = l_fqn
                    add_compat_alias(node_path,
                            '_'.join(l_cell_prefix + name + l_cell_name),
                            l_fqn, prop_alias)

                if node_path in aliases:
                    add_prop_aliases(
                        node_path,
                        lambda alias:
                            '_'.join([str_to_label(alias)] +
                                     l_cell_prefix + name + l_cell_name),
                        l_fqn,
                        prop_alias)

            index += 1
            insert_defs(node_path, prop_def, prop_alias)

##
# @brief Management information for interrupts.
interrupts = DTInterrupts()
