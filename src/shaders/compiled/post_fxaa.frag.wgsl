diagnostic(off, derivative_uniformity);

struct FxaaUniforms {
    texelSize: vec2<f32>,
    subpixelStrength: f32,
    padding: f32,
}

@group(2) @binding(0) 
var image: texture_2d<f32>;
@group(2) @binding(1) 
var linearSampler: sampler;
@group(3) @binding(0) 
var<uniform> unnamed: FxaaUniforms;
var<private> input_u002e_uv_1: vec2<f32>;
var<private> u0040_entryPointOutput: vec4<f32>;

fn main_1() {
    var local: array<f32, 10>;
    var local_1: array<f32, 10>;
    var phi_1234_: f32;
    var phi_1235_: vec2<f32>;
    var phi_1246_: bool;
    var phi_1244_: bool;
    var phi_1240_: f32;
    var phi_1239_: f32;
    var phi_1238_: vec2<f32>;
    var phi_1237_: vec2<f32>;
    var phi_1236_: i32;
    var phi_1261_: bool;
    var phi_1255_: f32;
    var phi_1252_: vec2<f32>;
    var phi_1262_: bool;
    var phi_1256_: f32;
    var phi_1253_: vec2<f32>;
    var local_2: vec2<f32>;
    var local_3: vec2<f32>;
    var local_4: vec2<f32>;
    var local_5: vec2<f32>;
    var local_6: f32;
    var local_7: f32;
    var phi_1243_: vec2<f32>;
    var phi_1250_: vec4<f32>;
    var local_8: bool;
    var local_9: bool;
    var local_10: f32;
    var local_11: f32;
    var local_12: vec2<f32>;
    var local_13: vec2<f32>;

    let _e38 = input_u002e_uv_1;
    switch bitcast<i32>(0u) {
        default: {
            let _e40 = textureSampleLevel(image, linearSampler, _e38, 0f);
            let _e42 = dot(_e40.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e44 = unnamed.texelSize;
            let _e47 = textureSampleLevel(image, linearSampler, (_e38 + (vec2<f32>(0f, -1f) * _e44)), 0f);
            let _e49 = dot(_e47.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e51 = unnamed.texelSize;
            let _e54 = textureSampleLevel(image, linearSampler, (_e38 + (vec2<f32>(0f, 1f) * _e51)), 0f);
            let _e56 = dot(_e54.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e58 = unnamed.texelSize;
            let _e61 = textureSampleLevel(image, linearSampler, (_e38 + (vec2<f32>(-1f, 0f) * _e58)), 0f);
            let _e63 = dot(_e61.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e65 = unnamed.texelSize;
            let _e68 = textureSampleLevel(image, linearSampler, (_e38 + (vec2<f32>(1f, 0f) * _e65)), 0f);
            let _e70 = dot(_e68.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e74 = max(_e42, max(max(_e49, _e56), max(_e63, _e70)));
            let _e79 = (_e74 - min(_e42, min(min(_e49, _e56), min(_e63, _e70))));
            if (_e79 < max(0.0312f, (_e74 * 0.125f))) {
                phi_1250_ = _e40;
                break;
            }
            let _e84 = unnamed.texelSize;
            let _e87 = textureSampleLevel(image, linearSampler, (_e38 + (vec2<f32>(-1f, -1f) * _e84)), 0f);
            let _e89 = dot(_e87.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e91 = unnamed.texelSize;
            let _e94 = textureSampleLevel(image, linearSampler, (_e38 + (vec2<f32>(1f, -1f) * _e91)), 0f);
            let _e96 = dot(_e94.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e98 = unnamed.texelSize;
            let _e101 = textureSampleLevel(image, linearSampler, (_e38 + (vec2<f32>(-1f, 1f) * _e98)), 0f);
            let _e103 = dot(_e101.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e105 = unnamed.texelSize;
            let _e107 = textureSampleLevel(image, linearSampler, (_e38 + _e105), 0f);
            let _e109 = dot(_e107.xyz, vec3<f32>(0.299f, 0.587f, 0.114f));
            let _e140 = (((abs(((_e89 + _e103) - (2f * _e63))) + (2f * abs(((_e49 + _e56) - (2f * _e42))))) + abs(((_e96 + _e109) - (2f * _e70)))) >= ((abs(((_e89 + _e96) - (2f * _e49))) + (2f * abs(((_e63 + _e70) - (2f * _e42))))) + abs(((_e103 + _e109) - (2f * _e56)))));
            let _e141 = select(_e63, _e49, _e140);
            let _e142 = select(_e70, _e56, _e140);
            let _e144 = abs((_e141 - _e42));
            let _e146 = abs((_e142 - _e42));
            let _e147 = (_e144 >= _e146);
            let _e151 = unnamed.texelSize[1u];
            let _e154 = unnamed.texelSize[0u];
            let _e155 = select(_e154, _e151, _e140);
            phi_1234_ = _e155;
            if _e147 {
                phi_1234_ = -(_e155);
            }
            let _e159 = phi_1234_;
            let _e161 = (0.5f * (_e42 + select(_e142, _e141, _e147)));
            if _e140 {
                phi_1235_ = vec2<f32>(_e38.x, (_e38.y + (_e159 * 0.5f)));
            } else {
                phi_1235_ = vec2<f32>((_e38.x + (_e159 * 0.5f)), _e38.y);
            }
            let _e175 = phi_1235_;
            let _e178 = unnamed.texelSize[0u];
            let _e182 = unnamed.texelSize[1u];
            let _e185 = select(vec2<f32>(0f, _e182), vec2<f32>(_e178, 0f), vec2(_e140));
            let _e186 = (max(_e144, _e146) * 0.25f);
            phi_1246_ = false;
            phi_1244_ = false;
            phi_1240_ = 0f;
            phi_1239_ = 0f;
            phi_1238_ = _e175;
            phi_1237_ = _e175;
            phi_1236_ = 0i;
            loop {
                let _e188 = phi_1246_;
                let _e190 = phi_1244_;
                let _e192 = phi_1240_;
                let _e194 = phi_1239_;
                let _e196 = phi_1238_;
                let _e198 = phi_1237_;
                let _e200 = phi_1236_;
                local_2 = _e198;
                local_3 = _e198;
                local_4 = _e196;
                local_5 = _e196;
                local_6 = _e194;
                local_7 = _e192;
                if (_e200 < 10i) {
                    phi_1261_ = _e190;
                    phi_1255_ = _e194;
                    phi_1252_ = _e198;
                    if !(_e190) {
                        local = array<f32, 10>(1f, 1f, 1f, 1f, 1.5f, 2f, 2f, 2f, 4f, 8f);
                        let _e204 = local[_e200];
                        let _e206 = (_e198 - (_e185 * _e204));
                        let _e207 = textureSampleLevel(image, linearSampler, _e206, 0f);
                        let _e210 = (dot(_e207.xyz, vec3<f32>(0.299f, 0.587f, 0.114f)) - _e161);
                        phi_1261_ = (abs(_e210) >= _e186);
                        phi_1255_ = _e210;
                        phi_1252_ = _e206;
                    }
                    let _e214 = phi_1261_;
                    let _e216 = phi_1255_;
                    let _e218 = phi_1252_;
                    local_9 = _e214;
                    local_11 = _e216;
                    local_13 = _e218;
                    phi_1262_ = _e188;
                    phi_1256_ = _e192;
                    phi_1253_ = _e196;
                    if !(_e188) {
                        local_1 = array<f32, 10>(1f, 1f, 1f, 1f, 1.5f, 2f, 2f, 2f, 4f, 8f);
                        let _e221 = local_1[_e200];
                        let _e223 = (_e196 + (_e185 * _e221));
                        let _e224 = textureSampleLevel(image, linearSampler, _e223, 0f);
                        let _e227 = (dot(_e224.xyz, vec3<f32>(0.299f, 0.587f, 0.114f)) - _e161);
                        phi_1262_ = (abs(_e227) >= _e186);
                        phi_1256_ = _e227;
                        phi_1253_ = _e223;
                    }
                    let _e231 = phi_1262_;
                    let _e233 = phi_1256_;
                    let _e235 = phi_1253_;
                    local_8 = _e231;
                    local_10 = _e233;
                    local_12 = _e235;
                    continue;
                } else {
                    break;
                }
                continuing {
                    let _e318 = local_8;
                    phi_1246_ = _e318;
                    let _e321 = local_9;
                    phi_1244_ = _e321;
                    let _e324 = local_10;
                    phi_1240_ = _e324;
                    let _e327 = local_11;
                    phi_1239_ = _e327;
                    let _e330 = local_12;
                    phi_1238_ = _e330;
                    let _e333 = local_13;
                    phi_1237_ = _e333;
                    phi_1236_ = (_e200 + 1i);
                }
            }
            let _e239 = local_2;
            let _e244 = local_3;
            let _e247 = select((_e38.y - _e244.y), (_e38.x - _e239.x), _e140);
            let _e249 = local_4;
            let _e254 = local_5;
            let _e258 = select((_e254.y - _e38.y), (_e249.x - _e38.x), _e140);
            let _e264 = local_6;
            let _e266 = local_7;
            let _e286 = smoothstep(0f, 1f, clamp((abs((((((((2f * (((_e49 + _e56) + _e63) + _e70)) + _e89) + _e96) + _e103) + _e109) * 0.083333336f) - _e42)) / _e79), 0f, 1f));
            let _e289 = unnamed.subpixelStrength;
            let _e291 = max(select(0f, (0.5f - (min(_e247, _e258) / (_e247 + _e258))), ((select(_e266, _e264, (_e247 < _e258)) < 0f) != (_e42 < _e161))), ((_e286 * _e286) * _e289));
            if _e140 {
                phi_1243_ = vec2<f32>(_e38.x, (_e38.y + (_e291 * _e159)));
            } else {
                phi_1243_ = vec2<f32>((_e38.x + (_e291 * _e159)), _e38.y);
            }
            let _e305 = phi_1243_;
            let _e306 = textureSampleLevel(image, linearSampler, _e305, 0f);
            phi_1250_ = vec4<f32>(_e306.x, _e306.y, _e306.z, _e40.w);
            break;
        }
    }
    let _e313 = phi_1250_;
    u0040_entryPointOutput = _e313;
    return;
}

@fragment 
fn main(@location(0) input_u002e_uv: vec2<f32>) -> @location(0) vec4<f32> {
    input_u002e_uv_1 = input_u002e_uv;
    main_1();
    let _e3 = u0040_entryPointOutput;
    return _e3;
}
