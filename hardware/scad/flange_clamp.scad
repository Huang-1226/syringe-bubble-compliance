// ============================================================
//  法兰夹 —— 从上方套下（方管），螺丝孔在 X 轴上
//  坐标：针筒轴 = X；法兰 = 垂直于 X 的"卡片"
//  ============================================================

// ---- 实测(占位) ----
flange_t = 1.28;  // 法兰厚(沿 X)
flange_w = 22;    // 槽 Y 向(法兰水平方向 19.5 + 余量)；法兰的 30 那面朝上下的 Z
barrel_d = 16.5;  // 筒身外径(10mL)
rod_d    = 13.44; // 活塞杆直径
axis_h   = 44;    // 轴心高度(底座上方；= 滑块顶面28.5 + 连轴夹腿15.5)

// ---- 结构 ----
jaw_t    = 5;     // 夹壁厚(X)
sw       = 4;     // 侧壁厚(Y)
H        = 60;    // 管体高（容纳 axis_h=44 处竖直 30 的法兰）
open_d   = 18;    // 前后开口大小(筒身16.5，留余量)
Bx       = 14;    // 底座 X 负向半宽
Bxp      = 36;    // 底座 X 正向(伸出去放螺丝孔)
Bt       = 6;     // 底座厚
hole_sp  = 20;    // 螺丝孔距(沿 X)
hole_d   = 6;     // 螺丝孔直径

$fn = 64;

// 法兰轮廓（YZ 平面内的圆润叶片形：19.5 宽 × 30 高，尖朝上下）+ 单边余量
flange_clr = 0.6;   // 凹槽相对法兰的单边余量
flange_pt = [ for (i = [0:119]) let(t = 360*i/120, c = cos(t), s = sin(t))
                [ (15+flange_clr)*sign(c)*pow(abs(c), 1.333), (9.75+flange_clr)*sign(s)*pow(abs(s), 1.333) ] ];

module flange_clamp() {
    Xw = flange_t/2 + jaw_t;    // 管体 X 半宽
    Yw = flange_w/2 + sw;       // 管体 Y 半宽

    difference() {
        union() {
            // 底板：从管体接出，连到螺丝孔那一块（Y 向尺寸 30）
            translate([5, -15, 0]) cube([25, 30, Bt]);
            // 管体
            translate([-Xw, -Yw, 0]) cube([2*Xw, 2*Yw, H]);
        }

        // 中央法兰凹槽：按法兰轮廓（圆润叶片形，竖放），薄片
        translate([0, 0, axis_h]) rotate([0,90,0])
            linear_extrude(height = flange_t + 0.6, center = true)
                polygon(points = flange_pt);
        // 下方直槽：便于从下往上把法兰套进去
        translate([-(flange_t + 0.6)/2, -(9.75+flange_clr), -1])
            cube([flange_t + 0.6, 2*(9.75+flange_clr), axis_h + 1]);

        // 下：留 6 高的空
        translate([-Xw - 1, -open_d/2, -1])
            cube([Xw + 1 - flange_t/2 + 1, open_d, 7]);
        translate([flange_t/2 - 1, -open_d/2, -1])
            cube([Xw + 1 - flange_t/2 + 1, open_d, 7]);

        // 上开口：弧形（按筒身圆做圆口）+ 向上开通到顶
        translate([-Xw - 1, 0, axis_h]) rotate([0,90,0])
            cylinder(d = open_d, h = Xw + 1 - flange_t/2 + 1);
        translate([-Xw - 1, -open_d/2, axis_h])
            cube([Xw + 1 - flange_t/2 + 1, open_d, H - axis_h + 2]);
        translate([flange_t/2 - 1, 0, axis_h]) rotate([0,90,0])
            cylinder(d = open_d, h = Xw + 1 - flange_t/2 + 1);
        translate([flange_t/2 - 1, -open_d/2, axis_h])
            cube([Xw + 1 - flange_t/2 + 1, open_d, H - axis_h + 2]);

        // 中间挖空（跨金属条 + 空隙 + 丝杆）：11 宽、24 高
        translate([-Xw - 1, -5.5, -1])
            cube([39, 11, 24]);

        // 2 个螺丝孔（关于 X 轴对称：x=+20, y=±10）
        for (sy = [-1, 1])
            translate([20, sy*hole_sp/2, -1])
                cylinder(d = hole_d, h = Bt + 2);
    }
}

flange_clamp();
// 样式对了再换实测尺寸
