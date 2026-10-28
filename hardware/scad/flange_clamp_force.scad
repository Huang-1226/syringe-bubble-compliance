// ============================================================
//  法兰夹 · 测力版 (输入侧)  v3
//  底部 20mm 收窄到 26；上部左右两条悬臂横跨夹持载荷条；
//  条槽【顶部全开】→ 条从上放下；两端用 4 个 M3 孔固定；
//  法兰上叶片从前方压条 → 读法兰反力 F_in。
//  ---- 用前改下面"实测"参数 ----
// ============================================================

$fn = 64;

show_bar = true;   // 预览用参考块；导出 STL 时用 -D show_bar=false 关掉

// ---- 针筒 / 法兰 (实测) ----
flange_t = 1.28;   // 法兰厚(X)
flange_w = 22;     // 法兰槽 Y 宽 = 19.5 + 余量
barrel_d = 16.5;   // 筒身外径
rod_d    = 13.44;  // 杆径
axis_h   = 44;     // 轴心高

// ---- 原结构 ----
jaw_t   = 5;       // 夹壁厚(X)
sw      = 4;       // 侧壁厚(Y)
H       = 60;      // 管体高
open_d  = 18;      // 筒身开口
Bt      = 6;       // 底板厚
hole_sp = 20;      // 螺丝孔距(硬要求, 保持20)
hole_d  = 4.5;     // M4 通孔(自攻丝可再收到 3.4)

// ---- 收窄 ----
leg_h = 20;        // 底部收窄段高
leg_w = 26;        // 底部收窄段 Y 宽 (原 30)

// ---- 载荷条 (实测 75×14×12；厚 12 朝 X = 受力向) ----
bar_l = 75;        // 长 (Y)
bar_w = 14;        // 宽 (Z)
bar_t = 12;        // 厚 (X)
bar_x = 7;         // 条中心 X
bar_z = 60;        // 条中心 Z (下沿53压在法兰上叶片区52.25~57，离筒身~0.75mm)
slot_x = 13;       // 条槽 X 宽 (略大于 12)

// ---- 载荷条螺孔 (实测) ----
scr_d  = 3.0;      // M3
hole_y1 = 22.5;    // 内侧孔离中心 (37.5-15)
hole_y2 = 32.5;    // 外侧孔离中心 (37.5-5)
scr_wall = 4.5;    // 固定面通孔(M4 过孔, 固定条的螺丝是4mm)

// ---- 悬臂 ----
arm_x0  = -6;      // 悬臂 X 起点 (兼作"固定面"背面)
arm_xw  = 24;      // 悬臂 X 宽
arm_h   = 18;      // 悬臂 Z 高 (开口在上)
arm_ext = 4;       // 悬臂伸出条端外(Y)
clr     = 0.3;     // 条与槽间隙

Xw   = flange_t/2 + jaw_t;
Yw   = flange_w/2 + sw;
Yend = bar_l/2 + arm_ext;      // = 41.5
wf   = bar_x - bar_t/2;        // 固定面 X = 1

flange_clr = 0.6;
flange_pt = [ for (i=[0:119]) let(t=360*i/120, c=cos(t), s=sin(t))
    [ (15+flange_clr)*sign(c)*pow(abs(c),1.333),
      (9.75+flange_clr)*sign(s)*pow(abs(s),1.333) ] ];

module clamp() {
    difference() {
        union() {
            // 底板
            translate([5, -leg_w/2, 0]) cube([25, leg_w, Bt]);
            // 下部(收窄到 leg_w)
            translate([-Xw, -leg_w/2, 0]) cube([2*Xw, leg_w, leg_h]);
            // 上部(原宽)
            translate([-Xw, -Yw, leg_h]) cube([2*Xw, 2*Yw, H-leg_h]);
            // 左右悬臂(在条的高度，向 ±Y 伸出) —— 兼作固定面
            for (s=[-1,1])
                translate([arm_x0, s>0 ? Yw : -Yend, bar_z-arm_h/2])
                    cube([arm_xw, Yend-Yw, arm_h]);
        }

        // 法兰凹槽
        translate([0,0,axis_h]) rotate([0,90,0])
            linear_extrude(flange_t+0.6, center=true) polygon(points=flange_pt);
        // 下直槽
        translate([-(flange_t+0.6)/2, -(9.75+flange_clr), -1])
            cube([flange_t+0.6, 2*(9.75+flange_clr), axis_h+1]);

        // 底部让位(筒身/下方)
        translate([-Xw-1, -open_d/2, -1]) cube([Xw+1-flange_t/2+1, open_d, 7]);
        translate([flange_t/2-1, -open_d/2, -1]) cube([Xw+1-flange_t/2+1, open_d, 7]);
        // 上开口(筒身)
        translate([-Xw-1,0,axis_h]) rotate([0,90,0]) cylinder(d=open_d, h=Xw+1-flange_t/2+1);
        translate([-Xw-1,-open_d/2,axis_h]) cube([Xw+1-flange_t/2+1, open_d, H-axis_h+2]);
        translate([flange_t/2-1,0,axis_h]) rotate([0,90,0]) cylinder(d=open_d, h=Xw+1-flange_t/2+1);
        translate([flange_t/2-1,-open_d/2,axis_h]) cube([Xw+1-flange_t/2+1, open_d, H-axis_h+2]);
        // 轨道通道
        translate([-Xw-1, -5.5, -1]) cube([39, 11, 24]);
        // 螺丝孔
        for (s=[-1,1]) translate([20, s*hole_sp/2, -1]) cylinder(d=hole_d, h=Bt+2);

        // ---- 削掉 +X 夹壁(法兰高度)：法兰只压条、不压夹壁(否则旁路→测不准) ----
        translate([flange_t/2, -(Yend), axis_h-16])
            cube([Xw+1, 2*Yend, 34]);

        // ---- 条槽：X 宽 slot_x、【顶部全开】→ 条从上放下 ----
        translate([wf, -(Yend), bar_z-(bar_w+clr)/2])
            cube([slot_x, 2*Yend, 80]);

        // ---- 固定面 4×M3 通孔(沿 X，两侧对称) ----
        for (s=[-1,1]) for (hy=[hole_y1, hole_y2])
            translate([arm_x0 - 1, s*hy, bar_z]) rotate([0,90,0])
                cylinder(d=scr_wall, h=arm_xw+2);
    }
}

clamp();

// ---- 载荷条(仅参考，打印时删掉这一段) ----
if (show_bar)
    color("orange", 0.6)
        translate([bar_x, 0, bar_z]) cube([bar_t, bar_l, bar_w], center=true);
