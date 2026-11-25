diagnostic(off, derivative_uniformity);

struct RcasUniforms {
    sharpness: f32,
    maxX: f32,
    maxY: f32,
    padding: f32,
}

@group(3) @binding(0) 
var<uniform> unnamed: RcasUniforms;
@group(2) @binding(0) 
var source: texture_2d<f32>;
@group(2) @binding(1) 
var sourceSampler: sampler;
var<private> input_u002e_pos_1: vec4<f32>;
var<private> input_u002e_uv_1: vec2<f32>;
var<private> u0040_entryPointOutput: vec4<f32>;

fn main_1() {
    let _e25 = input_u002e_pos_1;
    let _e26 = input_u002e_uv_1;
    let _e28 = vec2<i32>(_e25.xy);
    let _e31 = unnamed.maxX;
    let _e34 = unnamed.maxY;
    let _e37 = clamp((_e28 + vec2<i32>(0i, -1i)), vec2<i32>(0i, 0i), vec2<i32>(i32(_e31), i32(_e34)));
    let _e42 = textureLoad(source, vec3<i32>(_e37.x, _e37.y, 0i).xy, 0i);
    let _e43 = _e42.xyz;
    let _e46 = unnamed.maxX;
    let _e49 = unnamed.maxY;
    let _e52 = clamp((_e28 + vec2<i32>(-1i, 0i)), vec2<i32>(0i, 0i), vec2<i32>(i32(_e46), i32(_e49)));
    let _e57 = textureLoad(source, vec3<i32>(_e52.x, _e52.y, 0i).xy, 0i);
    let _e58 = _e57.xyz;
    let _e59 = textureSampleLevel(source, sourceSampler, _e26, 0f);
    let _e60 = _e59.xyz;
    let _e63 = unnamed.maxX;
    let _e66 = unnamed.maxY;
    let _e69 = clamp((_e28 + vec2<i32>(1i, 0i)), vec2<i32>(0i, 0i), vec2<i32>(i32(_e63), i32(_e66)));
    let _e74 = textureLoad(source, vec3<i32>(_e69.x, _e69.y, 0i).xy, 0i);
    let _e75 = _e74.xyz;
    let _e78 = unnamed.maxX;
    let _e81 = unnamed.maxY;
    let _e84 = clamp((_e28 + vec2<i32>(0i, 1i)), vec2<i32>(0i, 0i), vec2<i32>(i32(_e78), i32(_e81)));
    let _e89 = textureLoad(source, vec3<i32>(_e84.x, _e84.y, 0i).xy, 0i);
    let _e90 = _e89.xyz;
    let _e93 = min(min(_e43, min(_e58, _e75)), _e90);
    let _e96 = max(max(_e43, max(_e58, _e75)), _e90);
    let _e108 = max(-((min(_e93, _e60) / max((_e96 * 4f), vec3<f32>(0.000015258789f, 0.000015258789f, 0.000015258789f)))), ((vec3<f32>(1f, 1f, 1f) - max(_e96, _e60)) / min(((_e93 * 4f) - vec3<f32>(4f, 4f, 4f)), vec3<f32>(-0.000015258789f, -0.000015258789f, -0.000015258789f))));
    let _e117 = unnamed.sharpness;
    let _e118 = (max(-0.1875f, min(max(_e108.x, max(_e108.y, _e108.z)), 0f)) * _e117);
    let _e127 = ((((((_e43 + _e58) + _e75) + _e90) * _e118) + _e60) / vec3(((4f * _e118) + 1f)));
    u0040_entryPointOutput = vec4<f32>(_e127.x, _e127.y, _e127.z, 1f);
    return;
}

@fragment 
fn main(@builtin(position) input_u002e_pos: vec4<f32>, @location(0) input_u002e_uv: vec2<f32>) -> @location(0) vec4<f32> {
    input_u002e_pos_1 = input_u002e_pos;
    input_u002e_uv_1 = input_u002e_uv;
    main_1();
    let _e5 = u0040_entryPointOutput;
    return _e5;
}
