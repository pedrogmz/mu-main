diagnostic(off, derivative_uniformity);

struct EasuUniforms {
    con0_: vec4<f32>,
    con1_: vec4<f32>,
    con2_: vec4<f32>,
    con3_: vec4<f32>,
}

@group(3) @binding(0) 
var<uniform> unnamed: EasuUniforms;
@group(2) @binding(0) 
var source: texture_2d<f32>;
@group(2) @binding(1) 
var sourceSampler: sampler;
var<private> input_u002e_pos_1: vec4<f32>;
var<private> u0040_entryPointOutput: vec4<f32>;

fn main_1() {
    let _e30 = input_u002e_pos_1;
    let _e34 = unnamed.con0_;
    let _e38 = unnamed.con0_;
    let _e40 = ((floor(_e30.xy) * _e34.xy) + _e38.zw);
    let _e41 = floor(_e40);
    let _e42 = (_e40 - _e41);
    let _e44 = unnamed.con1_;
    let _e48 = unnamed.con1_;
    let _e50 = ((_e41 * _e44.xy) + _e48.zw);
    let _e52 = unnamed.con2_;
    let _e54 = (_e50 + _e52.xy);
    let _e56 = unnamed.con2_;
    let _e58 = (_e50 + _e56.zw);
    let _e60 = unnamed.con3_;
    let _e62 = (_e50 + _e60.xy);
    let _e63 = textureGather(0, source, sourceSampler, _e50);
    let _e64 = textureGather(1, source, sourceSampler, _e50);
    let _e65 = textureGather(2, source, sourceSampler, _e50);
    let _e66 = textureGather(0, source, sourceSampler, _e54);
    let _e67 = textureGather(1, source, sourceSampler, _e54);
    let _e68 = textureGather(2, source, sourceSampler, _e54);
    let _e69 = textureGather(0, source, sourceSampler, _e58);
    let _e70 = textureGather(1, source, sourceSampler, _e58);
    let _e71 = textureGather(2, source, sourceSampler, _e58);
    let _e72 = textureGather(0, source, sourceSampler, _e62);
    let _e73 = textureGather(1, source, sourceSampler, _e62);
    let _e74 = textureGather(2, source, sourceSampler, _e62);
    let _e78 = ((_e65 * 0.5f) + ((_e63 * 0.5f) + _e64));
    let _e82 = ((_e68 * 0.5f) + ((_e66 * 0.5f) + _e67));
    let _e86 = ((_e71 * 0.5f) + ((_e69 * 0.5f) + _e70));
    let _e90 = ((_e74 * 0.5f) + ((_e72 * 0.5f) + _e73));
    let _e107 = ((1f - _e42.x) * (1f - _e42.y));
    let _e112 = max(abs((_e86.w - _e82.z)), abs((_e82.z - _e82.w)));
    let _e116 = (_e86.w - _e82.w);
    let _e120 = clamp((abs(_e116) * select(0f, (1f / _e112), (_e112 > 0f))), 0f, 1f);
    let _e126 = max(abs((_e82.y - _e82.z)), abs((_e82.z - _e78.x)));
    let _e130 = (_e82.y - _e78.x);
    let _e134 = clamp((abs(_e130) * select(0f, (1f / _e126), (_e126 > 0f))), 0f, 1f);
    let _e141 = (_e42.x * (1f - _e42.y));
    let _e146 = max(abs((_e86.z - _e86.w)), abs((_e86.w - _e82.z)));
    let _e150 = (_e86.z - _e82.z);
    let _e155 = clamp((abs(_e150) * select(0f, (1f / _e146), (_e146 > 0f))), 0f, 1f);
    let _e163 = max(abs((_e86.x - _e86.w)), abs((_e86.w - _e78.y)));
    let _e167 = (_e86.x - _e78.y);
    let _e172 = clamp((abs(_e167) * select(0f, (1f / _e163), (_e163 > 0f))), 0f, 1f);
    let _e179 = ((1f - _e42.x) * _e42.y);
    let _e184 = max(abs((_e86.x - _e82.y)), abs((_e82.y - _e82.x)));
    let _e188 = (_e86.x - _e82.x);
    let _e193 = clamp((abs(_e188) * select(0f, (1f / _e184), (_e184 > 0f))), 0f, 1f);
    let _e201 = max(abs((_e90.w - _e82.y)), abs((_e82.y - _e82.z)));
    let _e205 = (_e90.w - _e82.z);
    let _e210 = clamp((abs(_e205) * select(0f, (1f / _e201), (_e201 > 0f))), 0f, 1f);
    let _e216 = (_e42.x * _e42.y);
    let _e221 = max(abs((_e86.y - _e86.x)), abs((_e86.x - _e82.y)));
    let _e225 = (_e86.y - _e82.y);
    let _e227 = ((((_e116 * _e107) + (_e150 * _e141)) + (_e188 * _e179)) + (_e225 * _e216));
    let _e230 = clamp((abs(_e225) * select(0f, (1f / _e221), (_e221 > 0f))), 0f, 1f);
    let _e238 = max(abs((_e90.z - _e86.x)), abs((_e86.x - _e86.w)));
    let _e242 = (_e90.z - _e86.w);
    let _e245 = vec2<f32>(_e227, ((((_e130 * _e107) + (_e167 * _e141)) + (_e205 * _e179)) + (_e242 * _e216)));
    let _e248 = clamp((abs(_e242) * select(0f, (1f / _e238), (_e238 > 0f))), 0f, 1f);
    let _e252 = (_e245 * _e245);
    let _e255 = (_e252.x + _e252.y);
    let _e256 = (_e255 < 0.000030517578f);
    let _e263 = (vec2<f32>(select(_e227, 1f, _e256), _e245.y) * select(inverseSqrt(_e255), 1f, _e256));
    let _e264 = ((((((((_e107 * ((_e120 * _e120) + (_e134 * _e134))) + ((_e155 * _e155) * _e141)) + ((_e172 * _e172) * _e141)) + ((_e193 * _e193) * _e179)) + ((_e210 * _e210) * _e179)) + ((_e230 * _e230) * _e216)) + ((_e248 * _e248) * _e216)) * 0.5f);
    let _e265 = (_e264 * _e264);
    let _e284 = vec2<f32>((1f + (((((_e263.x * _e263.x) + (_e263.y * _e263.y)) / max(abs(_e263.x), abs(_e263.y))) - 1f) * _e265)), (1f - (0.5f * _e265)));
    let _e286 = (0.5f + (-0.29f * _e265));
    let _e287 = (1f / _e286);
    let _e291 = vec3<f32>(_e66.z, _e67.z, _e68.z);
    let _e295 = vec3<f32>(_e69.w, _e70.w, _e71.w);
    let _e299 = vec3<f32>(_e66.y, _e67.y, _e68.y);
    let _e303 = vec3<f32>(_e69.x, _e70.x, _e71.x);
    let _e310 = (vec2<f32>(0f, -1f) - _e42);
    let _e331 = (vec2<f32>(((_e310.x * _e263.x) + (_e310.y * _e263.y)), ((_e310.x * -(_e263.y)) + (_e310.y * _e263.x))) * _e284);
    let _e339 = min(((_e331.x * _e331.x) + (_e331.y * _e331.y)), _e287);
    let _e341 = ((0.4f * _e339) - 1f);
    let _e343 = ((_e286 * _e339) - 1f);
    let _e348 = (((1.5625f * (_e341 * _e341)) - 0.5625f) * (_e343 * _e343));
    let _e350 = (vec2<f32>(1f, -1f) - _e42);
    let _e371 = (vec2<f32>(((_e350.x * _e263.x) + (_e350.y * _e263.y)), ((_e350.x * -(_e263.y)) + (_e350.y * _e263.x))) * _e284);
    let _e379 = min(((_e371.x * _e371.x) + (_e371.y * _e371.y)), _e287);
    let _e381 = ((0.4f * _e379) - 1f);
    let _e383 = ((_e286 * _e379) - 1f);
    let _e388 = (((1.5625f * (_e381 * _e381)) - 0.5625f) * (_e383 * _e383));
    let _e392 = (vec2<f32>(-1f, 1f) - _e42);
    let _e413 = (vec2<f32>(((_e392.x * _e263.x) + (_e392.y * _e263.y)), ((_e392.x * -(_e263.y)) + (_e392.y * _e263.x))) * _e284);
    let _e421 = min(((_e413.x * _e413.x) + (_e413.y * _e413.y)), _e287);
    let _e423 = ((0.4f * _e421) - 1f);
    let _e425 = ((_e286 * _e421) - 1f);
    let _e430 = (((1.5625f * (_e423 * _e423)) - 0.5625f) * (_e425 * _e425));
    let _e434 = (vec2<f32>(0f, 1f) - _e42);
    let _e451 = (vec2<f32>(((_e434.x * _e263.x) + (_e434.y * _e263.y)), ((_e434.x * -(_e263.y)) + (_e434.y * _e263.x))) * _e284);
    let _e459 = min(((_e451.x * _e451.x) + (_e451.y * _e451.y)), _e287);
    let _e461 = ((0.4f * _e459) - 1f);
    let _e463 = ((_e286 * _e459) - 1f);
    let _e468 = (((1.5625f * (_e461 * _e461)) - 0.5625f) * (_e463 * _e463));
    let _e472 = -(_e42);
    let _e489 = (vec2<f32>(((_e472.x * _e263.x) + (_e472.y * _e263.y)), ((_e472.x * -(_e263.y)) + (_e472.y * _e263.x))) * _e284);
    let _e497 = min(((_e489.x * _e489.x) + (_e489.y * _e489.y)), _e287);
    let _e499 = ((0.4f * _e497) - 1f);
    let _e501 = ((_e286 * _e497) - 1f);
    let _e506 = (((1.5625f * (_e499 * _e499)) - 0.5625f) * (_e501 * _e501));
    let _e510 = (vec2<f32>(-1f, 0f) - _e42);
    let _e531 = (vec2<f32>(((_e510.x * _e263.x) + (_e510.y * _e263.y)), ((_e510.x * -(_e263.y)) + (_e510.y * _e263.x))) * _e284);
    let _e539 = min(((_e531.x * _e531.x) + (_e531.y * _e531.y)), _e287);
    let _e541 = ((0.4f * _e539) - 1f);
    let _e543 = ((_e286 * _e539) - 1f);
    let _e548 = (((1.5625f * (_e541 * _e541)) - 0.5625f) * (_e543 * _e543));
    let _e552 = (vec2<f32>(1f, 1f) - _e42);
    let _e569 = (vec2<f32>(((_e552.x * _e263.x) + (_e552.y * _e263.y)), ((_e552.x * -(_e263.y)) + (_e552.y * _e263.x))) * _e284);
    let _e577 = min(((_e569.x * _e569.x) + (_e569.y * _e569.y)), _e287);
    let _e579 = ((0.4f * _e577) - 1f);
    let _e581 = ((_e286 * _e577) - 1f);
    let _e586 = (((1.5625f * (_e579 * _e579)) - 0.5625f) * (_e581 * _e581));
    let _e590 = (vec2<f32>(2f, 1f) - _e42);
    let _e611 = (vec2<f32>(((_e590.x * _e263.x) + (_e590.y * _e263.y)), ((_e590.x * -(_e263.y)) + (_e590.y * _e263.x))) * _e284);
    let _e619 = min(((_e611.x * _e611.x) + (_e611.y * _e611.y)), _e287);
    let _e621 = ((0.4f * _e619) - 1f);
    let _e623 = ((_e286 * _e619) - 1f);
    let _e628 = (((1.5625f * (_e621 * _e621)) - 0.5625f) * (_e623 * _e623));
    let _e632 = (vec2<f32>(2f, 0f) - _e42);
    let _e653 = (vec2<f32>(((_e632.x * _e263.x) + (_e632.y * _e263.y)), ((_e632.x * -(_e263.y)) + (_e632.y * _e263.x))) * _e284);
    let _e661 = min(((_e653.x * _e653.x) + (_e653.y * _e653.y)), _e287);
    let _e663 = ((0.4f * _e661) - 1f);
    let _e665 = ((_e286 * _e661) - 1f);
    let _e670 = (((1.5625f * (_e663 * _e663)) - 0.5625f) * (_e665 * _e665));
    let _e674 = (vec2<f32>(1f, 0f) - _e42);
    let _e691 = (vec2<f32>(((_e674.x * _e263.x) + (_e674.y * _e263.y)), ((_e674.x * -(_e263.y)) + (_e674.y * _e263.x))) * _e284);
    let _e699 = min(((_e691.x * _e691.x) + (_e691.y * _e691.y)), _e287);
    let _e701 = ((0.4f * _e699) - 1f);
    let _e703 = ((_e286 * _e699) - 1f);
    let _e708 = (((1.5625f * (_e701 * _e701)) - 0.5625f) * (_e703 * _e703));
    let _e712 = (vec2<f32>(1f, 2f) - _e42);
    let _e733 = (vec2<f32>(((_e712.x * _e263.x) + (_e712.y * _e263.y)), ((_e712.x * -(_e263.y)) + (_e712.y * _e263.x))) * _e284);
    let _e741 = min(((_e733.x * _e733.x) + (_e733.y * _e733.y)), _e287);
    let _e743 = ((0.4f * _e741) - 1f);
    let _e745 = ((_e286 * _e741) - 1f);
    let _e750 = (((1.5625f * (_e743 * _e743)) - 0.5625f) * (_e745 * _e745));
    let _e754 = (vec2<f32>(0f, 2f) - _e42);
    let _e775 = (vec2<f32>(((_e754.x * _e263.x) + (_e754.y * _e263.y)), ((_e754.x * -(_e263.y)) + (_e754.y * _e263.x))) * _e284);
    let _e783 = min(((_e775.x * _e775.x) + (_e775.y * _e775.y)), _e287);
    let _e785 = ((0.4f * _e783) - 1f);
    let _e787 = ((_e286 * _e783) - 1f);
    let _e792 = (((1.5625f * (_e785 * _e785)) - 0.5625f) * (_e787 * _e787));
    let _e799 = min(max(max(_e291, _e295), max(_e299, _e303)), max(min(min(_e291, _e295), min(_e299, _e303)), (((((((((((((vec3<f32>(_e63.x, _e64.x, _e65.x) * _e348) + (vec3<f32>(_e63.y, _e64.y, _e65.y) * _e388)) + (vec3<f32>(_e66.x, _e67.x, _e68.x) * _e430)) + (_e299 * _e468)) + (_e291 * _e506)) + (vec3<f32>(_e66.w, _e67.w, _e68.w) * _e548)) + (_e303 * _e586)) + (vec3<f32>(_e69.y, _e70.y, _e71.y) * _e628)) + (vec3<f32>(_e69.z, _e70.z, _e71.z) * _e670)) + (_e295 * _e708)) + (vec3<f32>(_e72.z, _e73.z, _e74.z) * _e750)) + (vec3<f32>(_e72.w, _e73.w, _e74.w) * _e792)) / vec3((((((((((((_e348 + _e388) + _e430) + _e468) + _e506) + _e548) + _e586) + _e628) + _e670) + _e708) + _e750) + _e792)))));
    u0040_entryPointOutput = vec4<f32>(_e799.x, _e799.y, _e799.z, 1f);
    return;
}

@fragment 
fn main(@builtin(position) input_u002e_pos: vec4<f32>) -> @location(0) vec4<f32> {
    input_u002e_pos_1 = input_u002e_pos;
    main_1();
    let _e3 = u0040_entryPointOutput;
    return _e3;
}
