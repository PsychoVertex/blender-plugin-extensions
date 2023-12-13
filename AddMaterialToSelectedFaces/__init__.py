import bpy


class AddMaterialToSelectedFacesOperator(bpy.types.Operator):
    bl_idname = "object.add_mat_sel_faces"
    bl_label = "Add Material to Selected Faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = bpy.context.active_object
        mesh = ob.data
        mat_len = len(mesh.materials)
        active_mat = ob.active_material

        mesh.materials.append(active_mat.copy())
        bpy.ops.object.mode_set(mode='OBJECT')
        for poly in mesh.polygons:
            if poly.select:
                poly.material_index = mat_len
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AddMaterialToSelectedFacesOperator)


def unregister():
    bpy.utils.unregister_class(AddMaterialToSelectedFacesOperator)
