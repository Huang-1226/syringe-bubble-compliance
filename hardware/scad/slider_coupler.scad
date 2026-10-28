// ============================================================
//  滑块联轴夹 v2 —— 夹住"活塞挡片"，实现 推 + 拉
//  几何：底板(拧在滑块上) 上长出 前后两片竖板，
//        两板之间夹住活塞挡片；前板开"杆槽"让活塞杆从上方落入。
//        推：挡片顶后板； 拉：挡片顶前板。
//  ============ 用前改下面"针筒实测"参数 ============
// ============================================================

// ---- 已知：模组滑块安装孔 ----
hole_sp = 20;     // 孔距 (mm)
mnt_d   = 3.4;    // M3 通孔 (mm)

// ---- 针筒实测（10mL）----
rod_d   = 8;      // 靠近挡片那段的杆宽(十字的窄段)，用于过杆孔
pad_d   = 17;     // 活塞挡片(圆盘)直径
pad_t   = 1.0;    // 活塞挡片厚度
axis_h  = 15.5;   // 夹子底面(滑块顶面) → 活塞杆轴心 = 44 − 28.5

// ---- 结构参数 ----
plate_p = 4;      // 竖板厚
base_t  = 6;      // 底板厚
pad_clr = 0.6;    // 挡片两侧间隙
rod_clr = 1.0;    // 杆槽间隙 → 过杆孔 = 8+1 = 9mm
top_m   = 6;      // 板顶高出挡片顶部的余量
W       = 32;     // 底板 X 向尺寸
Ysize   = 30;     // 底板 Y 向尺寸

$fn = 64;

module coupler() {
    gap  = pad_t + pad_clr;                 // 前后板内距 = 挡片厚 + 间隙
    yh   = Ysize/2;                          // Y 方向半宽 = 15
    ztop = axis_h + pad_d/2 + top_m;         // 竖板顶高

    f0 = -gap/2 - plate_p;                    // 前板外缘 x
    f1 = -gap/2;                             // 前板内缘 x
    b0 =  gap/2;                             // 后板内缘 x
    b1 =  gap/2 + plate_p;                   // 后板外缘 x

    difference() {
        union() {
            // 底板（前后板都从这里长出来 → 一体，不再是刀口接触）
            translate([-W/2, -yh, 0]) cube([W, 2*yh, base_t]);
            // 前板
            translate([f0, -yh, base_t]) cube([plate_p, 2*yh, ztop - base_t]);
            // 后板
            translate([b0, -yh, base_t]) cube([plate_p, 2*yh, ztop - base_t]);
        }
        // 4×M3 安装孔（你只用对角 2 个也行）
        for (sx = [-1,1]) for (sy = [-1,1])
            translate([sx*hole_sp/2, sy*hole_sp/2, -1])
                cylinder(d = mnt_d, h = base_t + 2);

        // 前板"杆槽"：从轴心向上开口，宽 = 杆径 + 间隙
        translate([f0 - 1, -(rod_d + rod_clr)/2, axis_h])
            cube([plate_p + 2, rod_d + rod_clr, ztop - axis_h + 2]);
        // 杆槽底部半圆让位
        translate([f0 + plate_p/2, 0, axis_h])
            rotate([0,90,0])
            cylinder(d = rod_d + rod_clr, h = plate_p + 2, center = true);
    }
}

coupler();
// 改好参数 → 导出 coupler.stl
