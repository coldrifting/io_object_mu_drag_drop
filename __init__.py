import bpy
import sys

bl_info = {
    "name": "Mu model format (KSP) Drag & Drop Import",
    "author": "coldrifting",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "category": "Import-Export",
}


class WM_FH_drag_and_drop_mu(bpy.types.FileHandler):
    bl_idname = "WM_FH_drag_and_drop_mu"
    bl_label = "Import MU"
    bl_import_operator = "wm.import_mu"
    bl_file_extensions = ".mu"

    @classmethod
    def poll_drop(cls, context):
        if context.space_data.type == "VIEW_3D":
            return True
        return False


def set_mesh_collider_wireframe():
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue

        props = obj.get('muproperties')
        if props is None:
            continue

        collider = props.get('collider')
        if collider is None:
            continue

        obj.display_type = 'WIRE'


def import_mu(context, filepath: str, create_colliders: bool, force_armature: bool, force_mesh: bool, set_collider_wireframe: bool):
    mu_module = sys.modules.get('io_object_mu')
    if mu_module is None:
        raise RuntimeError("No module named io_object_mu")

    mu_module.import_mu.operators.import_mu_op(
        self=mu_module.import_mu.operators,
        context=context,
        filepath=filepath,
        create_colliders=create_colliders,
        force_armature=force_armature,
        force_mesh=force_mesh)

    if set_collider_wireframe:
        set_mesh_collider_wireframe()


class WM_OT_ImportSettings(bpy.types.Operator):
    bl_idname = "wm.import_mu_settings"
    bl_label = "KSP (.Mu) Import Settings"
    bl_options = {'REGISTER', 'INTERNAL'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    mesh_collider_wireframe: bpy.props.BoolProperty(name="Mesh Colliders as Wireframe",
                                                    description="Import colliders with viewport display set to wireframe.",
                                                    default=True)
    create_colliders: bpy.props.BoolProperty(name="Create Colliders",
                                             description="Disable to import only visual and hierarchy elements.",
                                             default=True)
    force_armature: bpy.props.BoolProperty(name="Force Armature",
                                           description="Enable to force use of an armature to hold the model hierarchy.",
                                           default=False)
    force_mesh: bpy.props.BoolProperty(name="Force Invisible Mesh",
                                       description="Enable to force creation of mesh objects that have no renderer.",
                                       default=False)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "create_colliders")
        if self.create_colliders:
            layout.prop(self, "mesh_collider_wireframe")

        layout.prop(self, "force_armature")
        layout.prop(self, "force_mesh")

    def execute(self, context):
        import_mu(context,
                  filepath=self.filepath,
                  create_colliders=self.create_colliders,
                  force_armature=self.force_armature,
                  force_mesh=self.force_mesh,
                  set_collider_wireframe=self.mesh_collider_wireframe)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class ImportMu(bpy.types.Operator):
    bl_idname = "wm.import_mu"
    bl_label = "KSP (.Mu) Import"
    bl_description = "Install Addon"
    bl_options = {'INTERNAL'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    show_dialog = False

    def invoke(self, context, event):
        print("INVOKE_IMPORT")
        self.show_dialog = event.shift
        return self.execute(context)

    def execute(self, context):
        mu_module = sys.modules.get('io_object_mu')
        if mu_module is None:
            raise RuntimeError("No module named io_object_mu")

        if self.show_dialog:
            bpy.ops.wm.import_mu_settings('INVOKE_DEFAULT', filepath=self.filepath)
        else:
            import_mu(context,
                      filepath=self.filepath,
                      create_colliders=True,
                      force_armature=False,
                      force_mesh=False,
                      set_collider_wireframe=True)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(WM_OT_ImportSettings)
    bpy.utils.register_class(WM_FH_drag_and_drop_mu)
    bpy.utils.register_class(ImportMu)


def unregister():
    bpy.utils.unregister_class(WM_OT_ImportSettings)
    bpy.utils.unregister_class(WM_FH_drag_and_drop_mu)
    bpy.utils.unregister_class(ImportMu)
