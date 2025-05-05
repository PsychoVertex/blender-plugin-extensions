import bpy

WEIGHTED_NORMALS_MODIFIER_NAME = '__Weighted_Normal__'


def is_class_registered(class_type):
    try:
        bpy.utils.register_class(class_type)
    except Exception as e:
        if "already registered" in str(e):
            return True
    return False


def panel_exists(bl_idname):
    for panel_cls in bpy.types.Panel.__subclasses__():
        if not hasattr(panel_cls, "bl_idname"):
            continue
        if panel_cls.bl_idname != bl_idname:
            continue
        if is_class_registered(panel_cls):
            return True
    return False


class MZageHandyMenuSelectWeight(bpy.types.Operator):
    bl_idname = "mesh.mzage_select_weight"
    bl_label = "Select Weight"
    bl_description = "tooltip"
    bl_options = {"REGISTER"}

    strength: bpy.props.StringProperty(name="weight")

    def execute(self, context):
        bpy.ops.mesh.mod_weighted_strength(set=False, face_strength=self.strength)
        return {"FINISHED"}


class MZageHandyMenuSetWeight(bpy.types.Operator):
    bl_idname = "mesh.mzage_set_weight"
    bl_label = "Set Weight"
    bl_description = "tooltip"
    bl_options = {"REGISTER", "UNDO"}

    strength: bpy.props.StringProperty(name="weight")

    def execute(self, context):
        sos = context.selected_objects
        ao = context.active_object
        bpy.ops.mesh.mod_weighted_strength(set=True, face_strength=self.strength)
        bpy.ops.object.mode_set(mode='OBJECT')
        for so in sos:
            if not WEIGHTED_NORMALS_MODIFIER_NAME in [mod.name for mod in so.modifiers]:
                mesh = so.data
                sharpness = [edge.use_edge_sharp for edge in mesh.edges]
                context.view_layer.objects.active = so
                bpy.ops.object.shade_smooth(use_auto_smooth=True)
                bpy.ops.mesh.customdata_custom_splitnormals_add()
                for i, edge in enumerate(mesh.edges):
                    edge.use_edge_sharp = sharpness[i]

                mod = so.modifiers.new(name=WEIGHTED_NORMALS_MODIFIER_NAME, type='WEIGHTED_NORMAL')
                mod.mode = 'FACE_AREA_WITH_ANGLE'
                mod.weight = 100
                mod.keep_sharp = True
                mod.use_face_influence = True
                mod.show_on_cage = True
        bpy.ops.object.mode_set(mode='EDIT')
        context.view_layer.objects.active = ao
        return {"FINISHED"}


class MZageHandyMenu(bpy.types.Menu):
    bl_label = ""
    bl_idname = "OBJECT_MT_mzage_handy_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        ao = bpy.context.active_object
        if ao:
            mode = ao.mode
            if mode == "EDIT":
                row = layout.row()
                col = row.column()
                col.label(text="UV")
                col.operator("mesh.mark_seam", text="Mark Seam", icon="GREASEPENCIL")
                col.operator("mesh.mark_seam", text="Clear Seam", icon="OUTLINER_DATA_GP_LAYER").clear = True
                col.operator("uv.unwrap", text="Unwrap", icon="MOD_SHRINKWRAP")
                col.operator("uv.project_from_view", text="View Project", icon="PROP_PROJECTED").scale_to_bounds = False
                col.operator("uv.reset", text="Reset UVs", icon="X")
                col.separator()
                col.label(text="Mesh")
                if bpy.context.tool_settings.mesh_select_mode[1]:
                    col.operator("mesh.set_edge_flow", text="Set Flow", icon="SPHERECURVE")
                col.operator("mesh.mark_sharp", text="Mark Sharp", icon="GREASEPENCIL")
                col.operator("mesh.mark_sharp", text="Clear Sharp", icon="OUTLINER_DATA_GP_LAYER").clear = True
                if bpy.context.tool_settings.mesh_select_mode[2]:
                    col.operator("object.add_mat_sel_faces", text="Add Material", icon="MATERIAL")

                col = row.column()
                col.label(text="Normals")
                col.operator("mesh.flip_normals", text="Flip", icon="ORIENTATION_NORMAL")
                col.operator("mesh.normals_make_consistent", text="Recalculate", icon="NORMALS_VERTEX_FACE")
                col.operator("transform.rotate_normal", text="Rotate", icon="NORMALS_VERTEX")
                col.operator("mesh.normals_tools", text="Reset Normal", icon="SHADERFX").mode = "RESET"

                col.separator()
                col.operator(MZageHandyMenuSelectWeight.bl_idname, text="Select Weak", icon="RESTRICT_SELECT_ON").strength = 'WEAK'
                col.operator(MZageHandyMenuSelectWeight.bl_idname, text="Select Medium", icon="RESTRICT_SELECT_ON").strength = 'MEDIUM'
                col.operator(MZageHandyMenuSelectWeight.bl_idname, text="Select Strong", icon="RESTRICT_SELECT_ON").strength = 'STRONG'

                col.separator()
                col.operator(MZageHandyMenuSetWeight.bl_idname, text="Set Weak", icon="RESTRICT_SELECT_OFF").strength = 'WEAK'
                col.operator(MZageHandyMenuSetWeight.bl_idname, text="Set Medium", icon="RESTRICT_SELECT_OFF").strength = 'MEDIUM'
                col.operator(MZageHandyMenuSetWeight.bl_idname, text="Set Strong", icon="RESTRICT_SELECT_OFF").strength = 'STRONG'

                col = row.column()
                col.label(text="Selection")
                col.operator("mesh.loop_multi_select", text="Select Rings", icon="MESH_CIRCLE").ring = True
                col.operator("mesh.loop_multi_select", text="Select Loops", icon="STROKE").ring = False
                col.operator("mesh.region_to_loop", text="Select Boundary", icon="MOD_LATTICE")
                col.operator("mesh.loop_to_region", text="Select Inside", icon="OUTLINER_OB_LATTICE")
                col.operator("mesh.select_nth", text="Checker Deselect", icon="TEXTURE")
                if bpy.context.tool_settings.mesh_select_mode[2] and not bpy.context.tool_settings.mesh_select_mode[0] and not bpy.context.tool_settings.mesh_select_mode[1]:
                    col.operator("mesh.select_similar", text="Select Coplanar", icon="FACESEL").type = "COPLANAR"
                col.operator("mesh.select_overlapping_vertices", text="Overlap Vert", icon="VERTEXSEL")

                col.separator()
                col.label(text="Utils")
                col.operator("mesh.set_origin_to_selection", text="Origin to Selected", icon="OBJECT_ORIGIN")
                col.operator("mesh.set_origin_to_selection_and_rotate", text="Fix Rotation", icon="OBJECT_ORIGIN")
                col.operator("mesh.get_edge_length", icon="DRIVER_DISTANCE")
                col.operator("mesh.get_edges_angle", icon="DRIVER_ROTATIONAL_DIFFERENCE")
                # col.operator("mesh.snap_vertices_to_surface", icon="MOD_SHRINKWRAP")
            elif mode == "OBJECT":
                row = layout.row()
                col = row.column()

                col.label(text="Object")
                if ao.type == "MESH":
                    col.prop(ao, "display_type", text="", icon="NODE_MATERIAL")
                    col.prop(ao.data, "use_auto_smooth", icon="MOD_SMOOTH")
                col.operator("object.create_empty_parent", icon="EMPTY_DATA")
                col.operator("object.create_empty_parent_foreach", icon="EMPTY_DATA")
                if panel_exists("DATA_PT_PsychoHistory_KM"):
                    col.operator("wm.call_panel", text="Object History", icon="LOOP_BACK").name = "DATA_PT_PsychoHistory_KM"

                col.separator()
                col.label(text="Copy From Active")
                col.operator("object.make_links_data", text="Copy Modifiers", icon="MODIFIER").type = "MODIFIERS"
                col.operator("object.make_links_data", text="Copy Materials", icon="MATERIAL").type = "MATERIAL"

                col.separator()
                col.label(text="Copy To Active")
                col.operator("object.selected_origins_to_active", text="Origins To Active", icon="TRANSFORM_ORIGINS")

                col = row.column()
                col.label(text="Display Overlays")
                col.prop(context.area.spaces[0].overlay, "show_overlays", icon="OVERLAY")
                col.prop(context.area.spaces[0].overlay, "show_wireframes", icon="SHADING_WIRE")
                col.prop(context.area.spaces[0].overlay, "show_face_orientation", icon="FACESEL")
                col.separator()
                col.label(text="Import/Export")
                col.operator("import_scene.fbx", text="Import FBX", icon="IMPORT")
                col.operator("export_scene.fbx", text="Export FBX", icon="EXPORT")
                col.operator("object.batch_export_selections_as_sm", text="Batch Export SM_", icon="EXPORT")
                col.separator()
                col.label(text="To Unreal")
                col.operator("object.btus_setup", text="Setup for export", icon="SHADERFX")
                col.operator("object.btus_export", text="Set Export", icon="FAKE_USER_ON")
                col.operator("object.btus_dontexport", text="Set Dont Export", icon="FAKE_USER_OFF")
                col.operator("object.btus_updatepath", text="Update Path", icon="FILEBROWSER")
        else:
            if bpy.context.mode == "OBJECT":
                row = layout.row()
                col = row.column()
                col.label(text="Display Overlays")
                col.prop(context.area.spaces[0].overlay, "show_overlays", icon="OVERLAY")
                col.prop(context.area.spaces[0].overlay, "show_wireframes", icon="SHADING_WIRE")
                col.prop(context.area.spaces[0].overlay, "show_face_orientation", icon="FACESEL")
                col.separator()
                col.label(text="Import/Export")
                col.operator("import_scene.fbx", text="Import FBX", icon="IMPORT")
                col.operator("export_scene.fbx", text="Export FBX", icon="EXPORT")


classes = [
    MZageHandyMenuSelectWeight,
    MZageHandyMenuSetWeight,
    MZageHandyMenu
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
