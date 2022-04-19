#version 330 core
uniform sampler2D arpes_data;
uniform vec3 u_low_color;
uniform vec3 u_high_color;
// renders to screen
out vec4 fColor;

void main() {
  // 876,467
  float x = (gl_FragCoord.x-0.5)/876;
  float y = (gl_FragCoord.y-0.5)/467;
  float arpes_intensity = texture(arpes_data, vec2(x,y)).r;
  vec3 final_rgb = mix(u_low_color, u_high_color, arpes_intensity);
  // fColor = vec4(x,y,0,1);
  // fColor = vec4(0,0,1,1);
  fColor = vec4(final_rgb, 1);
}