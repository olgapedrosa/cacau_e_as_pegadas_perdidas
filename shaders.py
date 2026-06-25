"""
Shaders para renderização 3D com iluminação Phong
"""

VERTEX_SHADER = """
#version 410

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec2 texScale;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

void main()
{
    FragPos = vec3(model * vec4(position, 1.0));
    Normal = mat3(transpose(inverse(model))) * normal;
    // Allow scaling/repeating the texture via a uniform (set from Python)
    TexCoord = texCoord * texScale;
    
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 410

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

uniform sampler2D texture1;
uniform vec3 objectColor;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform bool useTexture;
uniform float brightnessBoost;

out vec4 FragColor;

void main()
{
    // Ambient
    float ambientStrength = 0.3;
    vec3 ambient = ambientStrength * lightColor;
    
    // Diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Specular
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = specularStrength * spec * lightColor;
    
    // Combinar iluminação
    vec3 result;
    float alpha = 1.0;
    if (useTexture) {
        vec4 texColor = texture(texture1, TexCoord);
        result = (ambient + diffuse + specular) * texColor.rgb;
        alpha = texColor.a;
    } else {
        result = (ambient + diffuse + specular) * objectColor;
    }

    result *= brightnessBoost;

    if (alpha < 0.05)
        discard;

    FragColor = vec4(result, alpha);
}
"""

def compile_shader(source, shader_type):
    """Compila um shader individual"""
    from OpenGL.GL import glCreateShader, glShaderSource, glCompileShader, glGetShaderiv, glGetShaderInfoLog, GL_COMPILE_STATUS
    
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        print(f"Erro ao compilar shader: {error}")
        return None
    
    return shader

def create_program():
    """Cria o programa de shader"""
    from OpenGL.GL import glCreateProgram, glAttachShader, glLinkProgram, glGetProgramiv, glGetProgramInfoLog, GL_LINK_STATUS, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
    
    vertex = compile_shader(VERTEX_SHADER, GL_VERTEX_SHADER)
    fragment = compile_shader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    
    program = glCreateProgram()
    glAttachShader(program, vertex)
    glAttachShader(program, fragment)
    glLinkProgram(program)
    
    if not glGetProgramiv(program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program).decode()
        print(f"Erro ao linkar programa: {error}")
        return None
    
    return program
