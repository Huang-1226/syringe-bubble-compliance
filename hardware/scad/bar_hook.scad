// ============================================================
//  载荷条挂钩 —— 拧在载荷条"自由端"的 2 个孔上
//  底板竖立(厚沿X)；螺丝孔沿 X(上下间距10)；横杆沿 +Y 伸出，球朝 +Y
//  钩头(带小球的杆)做成和 推杆挡片夹 一样: 杆 → 挡肩 → 凹槽 → 球
//  ---- 用前改下面"实测"参数 ----
// ============================================================

$fn = 64;

// ---- 实测 ----
hole_sp  = 10;     // 条自由端 2 孔间距(上下)
hole_d   = 4.5;    // M4 过孔(沿 X)
// ---- 结构 ----
plate_l  = 20;     // 板长(沿 Z)
plate_w  = 12;     // 板宽(沿 Y, 按金属条实际 12)
plate_t  = 2.5;    // 板厚(沿 X) — 法兰面到条面仅3mm间隙，取2.5留0.5
hook_len = 10;     // 杆+球 总长
hook_d   = 3.0;    // 杆径(原始值)
ball_d   = 4.0;    // 顶端小球(= 拉簧环内径 Ø4)
rod_l    = hook_len - ball_d/2;   // 杆长
groove_d = 2.2;    // 凹槽(颈)直径
groove_w = 1.5;    // 凹槽宽(≈ 拉簧线径)
flange_d = 4.4;    // 凹槽下方挡肩直径(稍大于环孔 Ø4, 把环卡住)
flange_h = 1.0;    // 挡肩厚
hook_z   = 0;      // 横杆中心高(相对孔心, 0=与孔心同高=离地36mm)
gy       = plate_w/2 + rod_l - ball_d/2 - 0.8 - groove_w;  // 凹槽底(球下 0.8, 沿杆)

module bar_hook() {
    difference() {
        union() {
            // 竖立底板: x 0..plate_t, y ±plate_w/2, z ±plate_l/2
            translate([0, -plate_w/2, -plate_l/2])
                cube([plate_t, plate_w, plate_l]);
            // 横杆：从板 +Y 边沿伸出，位于板厚中线(x=plate_t/2)、z=hook_z
            translate([plate_t/2, plate_w/2, hook_z]) rotate([-90,0,0])
                cylinder(d=hook_d, h=rod_l);
            // 顶端小球(朝 +Y)
            translate([plate_t/2, plate_w/2+rod_l, hook_z]) sphere(d=ball_d);
            // 挡肩(凹槽下方): 与顶球一起把拉簧圆环卡在凹槽里
            translate([plate_t/2, gy - flange_h, hook_z]) rotate([-90,0,0])
                cylinder(d=flange_d, h=flange_h);
        }
        // 2×M4 沿 X，间距 hole_sp
        for (sz=[-1,1])
            translate([-1, 0, sz*hole_sp/2]) rotate([0,90,0])
                cylinder(d=hole_d, h=plate_t+2);
        // (凹槽/颈已取消 → 防断)
    }
}

bar_hook();
// 导出 bar_hook.stl
