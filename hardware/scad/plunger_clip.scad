// ============================================================
//  推杆挡片夹 v5 —— 参考"滑块联轴夹"样式
//  * 凹槽(外框)统一按 10mL 做 → 5/10/20mL 三种挡片都能卡进这个框
//  * 十字杆开口仍按 WHICH 对应尺寸
//  * 钩子：只保留 Z 向竖杆(去掉 X 向部分)，装在后挡板上
//  ---- 换针筒只改 WHICH ----
// ============================================================

$fn = 64;

WHICH = 2;   // 1 = 5mL, 2 = 10mL, 3 = 20mL

// ---- 实测(按 WHICH 取) ----
pad_d    = (WHICH==1) ? 15.5 : (WHICH==2) ? 17.0 : 22.4;   // 挡片直径
pad_t    = (WHICH==1) ? 1.00 : (WHICH==2) ? 1.00 : 1.58;   // 挡片厚度(实测)
rod_d    = (WHICH==1) ? 7.26 : (WHICH==2) ? 8.00 : 13.0;   // 十字杆宽度
barrel_d = (WHICH==1) ? 14.00 : (WHICH==2) ? 16.68 : 20.70; // 输入针筒外径

// ---- 凹槽外框统一按 10mL ----
pad_d_fix = 17;

// ---- 结构 ----
pad_clr = -0.1;               // 负值=过盈(塞紧); 挡片厚 + pad_clr
gap     = pad_t + pad_clr;    // 两板内距 = 挡片厚 − 0.1(夹紧)
plate_t = 4;                  // 板厚(X)
Yw      = pad_d_fix/2 + 6;    // 14.5 → 框宽 29, 容得下 5/10/20 挡片
Zt      =  11;                // 板顶 = 钩底(hook_z), 让钩子接在板上
Zb      = -(pad_d_fix/2 + 1); // -9.5 (砍掉下方多余, 夹子可悬空)
base_t  = 5;                  // 底板厚

// ---- 钩子(竖杆+顶球) + 卡槽(卡住拉簧圆环) ----
hook_d   = 3.8;    // 上段圆杆径(加粗; 上限受顶球 Ø4 限制)
ball_d   = 4.0;    // 顶球径(= 拉簧环内径 Ø4)
groove_d = 3.2;    // 钩上凹槽(颈)直径(浅颈, 不当薄弱点)
shank_x  = plate_t;   // 钩杆下半段改成"板": 厚(X, 与后板同)
shank_w  = 2*Yw;      // 钩杆下半段: 宽(Y) = 整个后板宽度
groove_w = 1.5;    // 钩上凹槽宽(≈ 拉簧线径)
flange_d = 4.4;    // 凹槽下方挡肩直径(稍大于环孔 Ø4, 把环卡住)
flange_h = 1.0;    // 挡肩厚
// 两钩等高: 钩球中心离地高 HOOK_H = 载荷条挂钩(孔心36 + 板边6 + 杆8 = 50)
HOOK_H       = 50;
pad_center_h = 36 - 0.5 - barrel_d;    // 挡片中心(=推杆轴)离地高 = 36 − 0.5 − 针筒外径
hook_fix     = (WHICH==1) ? 7.5 : 4.0; // 实测补偿: 钩比金属条钩低的量(5mL 7.5, 10/20mL 4)
hook_top     = HOOK_H - pad_center_h + hook_fix;  // 球心相对挡片中心的高度
hook_base    = Zt - 4;                 // 杆底(埋进板里 4mm, 保证与板相连)
rod_l        = hook_top - hook_base;   // 杆长(挡片中心越低 → 杆自动越长)
groove_z     = hook_top - ball_d/2 - 0.8 - groove_w;   // 凹槽底(球下 0.8)

X0  = gap/2;              // 外(后)板内面
X1  = gap/2 + plate_t;    // 外(后)板外面
Xi0 = -gap/2 - plate_t;   // 内(前)板外面
Xh  = X0 + plate_t/2;     // 后挡板中面(竖杆落点)

module clip() {
    difference() {
        union() {
            // 底板
            translate([Xi0, -Yw, Zb]) cube([X1-Xi0, 2*Yw, base_t]);
            // 内(前)板
            translate([Xi0, -Yw, Zb]) cube([plate_t, 2*Yw, Zt-Zb]);
            // 外(后)板
            translate([X0, -Yw, Zb]) cube([plate_t, 2*Yw, Zt-Zb]);
            // 钩子: 下半段用"板"(杆底→挡肩下), 防根部拉断
            translate([Xh - shank_x/2, -shank_w/2, hook_base])
                cube([shank_x, shank_w, (groove_z - flange_h) - hook_base]);
            // 挡肩
            translate([Xh, 0, groove_z - flange_h]) cylinder(d=flange_d, h=flange_h);
            // 上段(凹槽+球)圆杆
            translate([Xh, 0, groove_z]) cylinder(d=hook_d, h=hook_top - groove_z);
            // 顶球
            translate([Xh, 0, hook_top]) sphere(d=ball_d);
        }
        // 内板"杆槽": 从顶部开到十字杆中心以下, 让整根十字杆通过
        translate([Xi0-1, -(rod_d+1)/2, -(rod_d/2+1)])
            cube([plate_t+2, rod_d+1, Zt+2+rod_d/2+1]);
        // (凹槽/颈已取消 → 防断)
    }
}

clip();
// 导出 plunger_clip.stl
