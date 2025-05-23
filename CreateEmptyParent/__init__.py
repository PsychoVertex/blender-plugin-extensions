import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from itertools import product


class CreateEmptyParentOperator(bpy.types.Operator):
    bl_idname = "object.create_empty_parent"
    bl_label = "Create Empty Parent"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(context.selected_objects) > 0

    def execute(self, context):
        ao = context.active_object
        so = context.selected_objects
        ac = ao.users_collection[0]

        empty = bpy.data.objects.new("empty", None)
        ac.objects.link(empty)
        empty.empty_display_size = max(0.1, max(ao.dimensions) * 1.1)
        empty.location = ao.location
        empty.parent = ao.parent
        empty.matrix_parent_inverse = ao.matrix_parent_inverse
        empty.name = f"{ao.name}_Parent"

        for s in so:
            s.parent = empty
            s.matrix_parent_inverse = empty.matrix_world.inverted()
            s.location = s.location - empty.location

        return {'FINISHED'}


class CreateEmptyParentForEachOperator(bpy.types.Operator):
    bl_idname = "object.create_empty_parent_foreach"
    bl_label = "Create Empty Parent (Foreach)"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        sos = context.selected_objects
        for so in sos:
            name = so.name
            so.name = f"{name}_Mesh"
            empty = bpy.data.objects.new(name, None)
            so.users_collection[0].objects.link(empty)

            empty.empty_display_size = max(0.1, max(so.dimensions) * 1.1)
            empty.location = so.location
            empty.parent = so.parent
            empty.matrix_parent_inverse = so.matrix_parent_inverse

            so.parent = empty
            so.matrix_parent_inverse = empty.matrix_world.inverted()
            so.location = so.location - empty.location
        return {'FINISHED'}


class CreateEmptyParentActiveOperator(bpy.types.Operator):
    bl_idname = "object.create_empty_parent_active"
    bl_label = "Create Empty Parent (Active)"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(context.selected_objects) > 0

    def execute(self, context):
        ao = context.active_object
        so = context.selected_objects
        ac = ao.users_collection[0]

        name = ao.name

        for s in so:
            s.name = f"{s.name}_Mesh"

        empty = bpy.data.objects.new("empty", None)
        ac.objects.link(empty)
        empty.empty_display_size = max(0.1, max(ao.dimensions) * 1.1)
        empty.location = ao.location
        empty.parent = ao.parent
        empty.matrix_parent_inverse = ao.matrix_parent_inverse
        empty.name = name

        for s in so:
            s.parent = empty
            s.matrix_parent_inverse = empty.matrix_world.inverted()
            s.location = s.location - empty.location

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CreateEmptyParentOperator)
    bpy.utils.register_class(CreateEmptyParentForEachOperator)
    bpy.utils.register_class(CreateEmptyParentActiveOperator)

def unregister():
    bpy.utils.unregister_class(CreateEmptyParentOperator)
    bpy.utils.unregister_class(CreateEmptyParentForEachOperator)
    bpy.utils.unregister_class(CreateEmptyParentActiveOperator)
