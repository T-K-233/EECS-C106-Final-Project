import time

import bpy

ROT_MODE = "QUATERNION"

# get the blender scene objects
armature = bpy.data.objects["Armature"]


bone0 = armature.pose.bones.get("Bone")
bone0.rotation_mode = ROT_MODE

bone1 = armature.pose.bones.get("Bone.001")
bone1.rotation_mode = ROT_MODE

bone2 = armature.pose.bones.get("Bone.002")
bone2.rotation_mode = ROT_MODE

class ModalTimerOperator(bpy.types.Operator):
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def __init__(self):
        pass

    def modal(self, context, event):
        global stop_flag

        # 按下 ESC 之后退出程序
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
#            print(int(time.time()) % 100, )
            print(bone2.head, bone2.tail, bone2.rotation_mode, bone2.rotation_quaternion)

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        print("END!")
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


print(dir(bone2))

bpy.utils.register_class(ModalTimerOperator)

bpy.ops.wm.modal_timer_operator()
