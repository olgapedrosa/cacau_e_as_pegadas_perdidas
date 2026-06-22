/** Shaders GLSL com iluminação Phong. */
const Shaders = {
  vertexSource: `#version 300 es
precision highp float;

in vec3 aPosition;
in vec3 aNormal;
in vec2 aTexCoord;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;
uniform mat4 uNormalMatrix;

out vec3 vFragPos;
out vec3 vNormal;
out vec2 vTexCoord;

void main() {
  vec4 worldPos = uModel * vec4(aPosition, 1.0);
  vFragPos = worldPos.xyz;
  vNormal = mat3(uNormalMatrix) * aNormal;
  vTexCoord = aTexCoord;
  gl_Position = uProjection * uView * worldPos;
}
`,

  fragmentSource: `#version 300 es
precision highp float;

in vec3 vFragPos;
in vec3 vNormal;
in vec2 vTexCoord;

uniform vec3 uViewPos;
uniform vec3 uLightPos;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform float uShininess;
uniform float uSpecularStrength;
uniform vec4 uSolidColor;
uniform sampler2D uTexture;
uniform int uUseTexture;
uniform int uUseSolidColor;
uniform float uAlpha;
uniform float uTime;
uniform int uAnimatedWater;

out vec4 fragColor;

void main() {
  vec3 baseColor;
  if (uUseSolidColor == 1) {
    baseColor = uSolidColor.rgb;
  } else if (uUseTexture == 1) {
    vec2 uv = vTexCoord;
    if (uAnimatedWater == 1) {
      uv.x += sin(uTime * 0.8 + vFragPos.z * 0.3) * 0.02;
      uv.y += cos(uTime * 0.6 + vFragPos.x * 0.3) * 0.02;
    }
    baseColor = texture(uTexture, uv).rgb;
  } else {
    baseColor = vec3(0.7);
  }

  vec3 norm = normalize(vNormal);
  vec3 lightDir = normalize(uLightPos - vFragPos);
  vec3 viewDir = normalize(uViewPos - vFragPos);

  float ambientStrength = 0.25;
  vec3 ambient = ambientStrength * uAmbientColor * baseColor;

  float diff = max(dot(norm, lightDir), 0.0);
  vec3 diffuse = diff * uLightColor * baseColor;

  vec3 reflectDir = reflect(-lightDir, norm);
  float spec = pow(max(dot(viewDir, reflectDir), 0.0), uShininess);
  vec3 specular = uSpecularStrength * spec * uLightColor;

  vec3 result = ambient + diffuse + specular;
  fragColor = vec4(result, uAlpha);
}
`,

  skyVertexSource: `#version 300 es
precision highp float;

in vec3 aPosition;
uniform mat4 uView;
uniform mat4 uProjection;

out vec3 vDir;

void main() {
  vDir = aPosition;
  vec4 pos = uProjection * mat4(mat3(uView)) * vec4(aPosition, 1.0);
  gl_Position = pos.xyww;
}
`,

  skyFragmentSource: `#version 300 es
precision highp float;

in vec3 vDir;
uniform vec3 uTopColor;
uniform vec3 uBottomColor;
uniform float uTime;

out vec4 fragColor;

void main() {
  float t = clamp(vDir.y * 0.5 + 0.5, 0.0, 1.0);
  vec3 sky = mix(uBottomColor, uTopColor, t);
  float sunGlow = pow(max(dot(normalize(vDir), normalize(vec3(
    cos(uTime * 0.08) * 0.6,
    0.45 + sin(uTime * 0.04) * 0.15,
    sin(uTime * 0.08) * 0.6
  ))), 0.0), 32.0);
  sky += vec3(1.0, 0.85, 0.5) * sunGlow * 0.6;
  fragColor = vec4(sky, 1.0);
}
`,
};
