# Three.js Visual Showcases and Advanced Techniques Research

A comprehensive deep-dive into award-winning Three.js projects, cutting-edge visual techniques, and production-proven optimization strategies. This research documents the most impressive visual showcases and the specific techniques that make them exceptional.

---

## Table of Contents

1. [Award-Winning Showcases and Demos](#award-winning-showcases-and-demos)
2. [Three.js Community and Learning Resources](#threejs-community-and-learning-resources)
3. [Bruno Simon's Three.js Journey Course](#bruno-simons-threejs-journey-course)
4. [React Three Fiber (R3F) Ecosystem](#react-three-fiber-r3f-ecosystem)
5. [Three.js Game Projects](#threejs-game-projects)
6. [AI-Assisted Three.js Workflows](#ai-assisted-threejs-workflows)
7. [Advanced Visual Techniques](#advanced-visual-techniques)
8. [Performance Optimization Strategies](#performance-optimization-strategies)
9. [Specific Implementation Deep-Dives](#specific-implementation-deep-dives)

---

## Award-Winning Showcases and Demos

### Overview

Three.js has powered numerous award-winning websites and demos that showcase cutting-edge web 3D capabilities. The best examples demonstrate not just technical prowess but also creative visual design.

### Key Showcase Platforms and Collections

- **Awwwards Three.js Collection**: The primary hub for award-winning Three.js websites, featuring sites that have won Awwwards recognition for innovation and design
  - URL: https://www.awwwards.com/websites/three-js/
  - Collections: https://www.awwwards.com/awwwards/collections/three-js/

- **The FWA (Favorite Website Awards)**: Recognizes exceptional Three.js projects
  - URL: https://thefwa.com/

- **Orpetron Collections**: Curated award-winning Three.js projects
  - 10 Award-Winning Projects: https://orpetron.com/blog/10-award-winning-projects-showcasing-three-js-innovation/
  - 10 Exceptional Websites: https://orpetron.com/blog/10-exceptional-websites-showcasing-creative-usage-of-threejs/

- **One Page Love**: Curated collection of 23 Three.js websites with full screenshots
  - URL: https://onepagelove.com/tag/three-js

### Notable 2024-2025 Award-Winning Projects

#### Jordan Breton's Floating Island Portfolio
- **Award**: FWA Site of the Day (October 2, 2025)
- **Visual Elements**: Floating island in sky with grass, waterfalls, fire, and butterflies
- **Techniques**:
  - Multi-angle navigation through 3D scene
  - Natural element rendering (vegetation, water effects, fire particles)
  - Interactive camera controls for exploration

#### JReyes MC's Minecraft-Inspired 3D Portfolio
- **Award**: Awwwards Honorable Mention
- **Visual Elements**: Circuit-based navigation through Minecraft-style 3D blocks
- **Techniques**:
  - Block-based geometry (optimized for instancing)
  - Theme-based scene separation
  - Interactive waypoint navigation

#### Samsy's Cyberpunk Portfolio (WebGPU)
- **Achievement**: 120+ FPS neon-lit cityscape
- **Technologies**: WebGPU, React Three Fiber
- **Key Techniques**:
  - Modern rendering API (WebGPU)
  - Real-time neon glow effects
  - High-performance city generation
  - Cyberpunk aesthetic with volumetric effects

#### Sector 32 Sci-Fi Portfolio
- **Visual Style**: Dark sci-fi interface with reflective chrome
- **Elements**: Reflective chrome skull, cyan laser beams, retro terminal UI
- **Technology Stack**: React Three Fiber (R3F)
- **Techniques**:
  - Reflective material rendering
  - Laser beam particle effects
  - UI integration with 3D scene
  - Animated corner ornaments

### What Makes These Showcases Visually Impressive

1. **Innovative Visual Design**: Award-winning projects combine 3D technical mastery with artistic vision
2. **High Performance**: Many run at 60+ FPS despite complex visuals
3. **Interactivity**: User control and responsive camera systems enhance immersion
4. **Atmosphere**: Lighting, color grading, and visual polish create memorable experiences
5. **Technical Innovation**: Use of WebGPU, advanced shaders, and optimization techniques push boundaries

**Resources**:
- https://webflow.com/made-in-webflow/threejs
- https://threejsresources.com/showcase
- https://www.creativedevjobs.com/blog/best-threejs-portfolio-examples-2025

---

## Three.js Community and Learning Resources

### Codrops Advanced Tutorials

Codrops (Tympanus) is a premier source for advanced Three.js techniques and tutorials.

#### Featured Advanced Topics

**WebGL & Shaders**
- Scroll-driven WebGL galleries with depth-layered images and palette-driven backgrounds
- Building curved 3D product grids with React Three Fiber and GLSL
- GPU-powered WebGL galleries with custom shaders

**Advanced Rendering Techniques**
- Composite rendering in WebGL using render targets for seamless transitions
- Video projection mapping simulation in digital environments
  - Technique: UV-mapping video textures and applying masks
- Screen-space effects and advanced compositing

**Interactive Effects**
- Scroll-driven, infinitely looping 3D image tubes using shaders and inertia
- Interactive 3D text destruction effects using Three.js, WebGPU, and TSL
- Voxelized video pixels dropped into physics-driven worlds

**Integration with Tools**
- Multi-page WebGL galleries with scroll-triggered shader reveals
- Seamless page transitions using GSAP, Three.js, Astro, and Barba.js

**URL**: https://tympanus.net/codrops/tag/three-js/

#### Notable Codrops Articles

1. **Building Efficient Three.js Scenes** (Feb 2025)
   - Optimizing performance while maintaining visual quality
   - URL: https://tympanus.net/codrops/2025/02/11/building-efficient-three-js-scenes-optimize-performance-while-maintaining-quality/

2. **Interactive Video Projection Mapping with Three.js** (Aug 2025)
   - Real-time video texture mapping and effects
   - URL: https://tympanus.net/codrops/2025/08/28/interactive-video-projection-mapping-with-three-js/

3. **Interactive Text Destruction with Three.js, WebGPU, and TSL** (July 2025)
   - Modern shader language techniques
   - URL: https://tympanus.net/codrops/2025/07/22/interactive-text-destruction-with-three-js-webgpu-and-tsl/

4. **Building a Fully-Featured 3D World in Blender and Three.js** (April 2025)
   - End-to-end asset creation and integration
   - URL: https://tympanus.net/codrops/2025/04/08/3d-world-in-the-browser-with-blender-and-three-js/

5. **Cyberpunk inspired Three.js Scene with JavaScript and Blender** (March 2023)
   - Visual style and post-processing for cinematic look
   - URL: https://tympanus.net/codrops/2023/03/22/cyberpunk-inspired-three-js-scene-with-javascript-and-blender/

6. **Crafting Scroll Based Animations in Three.js** (Jan 2022)
   - Interactive scroll-based 3D animation
   - URL: https://tympanus.net/codrops/2022/01/05/crafting-scroll-based-animations-in-three-js/

7. **Case Study: Windland — An Immersive Three.js Experience** (April 2022)
   - Production project breakdown and techniques
   - URL: https://tympanus.net/codrops/2022/04/25/case-study-windland-an-immersive-three-js-experience/

### Dev.to and Medium Advanced Articles

**DEV Community**
- Learning Three.js in 2024: https://dev.to/ankitakanchan/learning-threejs-in-2024-40id
- A Deep Dive into Three.js: https://dev.to/mohith/a-deep-dive-into-threejs-exploring-the-beauty-of-3d-on-the-web-5812
- Optimizing Three.js: 4 Key Techniques: https://dev.to/didof/optimizing-threejs-4-key-techniques-4lad
- Cyberpunk 3D Digital Earth: https://dev.to/dragonir/use-threejs-to-achieve-a-cool-cyberpunk-style-3d-digital-earth-screen-1fep

**Medium**
- Top 10 Advanced Three.js Tricks for 2024: https://medium.com/@AALA-IT-Solutions/top-10-advanced-three-js-tricks-for-2024-56fd065aed07
- Learning Three.js in 2024 - A Fun and Easy Way: https://medium.com/@ankitakanchan97/learning-three-js-in-2024-a-fun-and-easy-way-to-creating-3d-experiences-3f465801b171
- Experimenting with PBR Textures: https://medium.com/@Makoto_29712/experimenting-with-pbr-textures-usingthree-js-a25aad28ed65

### Three.js Resources and Demos

- Three.js Demos: https://threejsdemos.com/
- Three.js Resources Showcase: https://threejsresources.com/showcase
- Free Frontend Examples: https://freefrontend.com/three-js/

---

## Bruno Simon's Three.js Journey Course

### Course Overview

[Bruno Simon's Three.js Journey](https://threejs-journey.com/) is widely recognized as one of the most complete learning resources for Three.js, featuring more than 30 lessons covering the basics to advanced 3D techniques.

### Course Structure

The curriculum is organized progressively, with each lesson building on the previous one to create real-world projects. The teaching style is clear, concise, and visual, making complex topics accessible.

### Key Lesson Topics and Techniques

#### Foundational Concepts
- Cameras and camera controls
- Geometries and primitives
- Materials and material properties
- Textures and texture mapping

#### Intermediate Techniques
- Shaders and custom shader creation
- Animations and animation loops
- Lighting (directional, point, spotlights)
- Physics simulation
- Particle systems

#### Advanced Techniques
- **Baking**: Rendering the full lit scene onto UV coordinates using Blender
  - Technique: Save complicated lighting information into texture maps
  - Benefit: Reduce real-time lighting calculations for better performance
  - URL: https://threejs-journey.com/lessons/baking-and-exporting-the-scene

- **Realistic Rendering**: Physically-based materials and lighting
  - URL: https://threejs-journey.com/lessons/realistic-render

- **Textures**: Comprehensive texture handling and optimization
  - URL: https://threejs-journey.com/lessons/textures

- **Post-Processing**: Effects like bloom, depth of field, and motion blur
  - URL: https://threejs-journey.com/lessons/post-processing

- **React Three Fiber (R3F)**: Declarative 3D with React
  - Integration with React ecosystem
  - Component-based scene building
  - State management patterns

- **Environment Maps**: HDRI and IBL techniques
  - URL: https://threejs-journey.com/lessons/environment-map

#### Interaction Techniques
- Raycaster for detecting object interactions
- Camera controls (Orbit Control recommended as starting point)
- Mouse and keyboard input handling

### Course Awards

- FWA Site of the Day recognition
- Community as Gold Standard for Three.js education

### Implementation Strategy from the Course

The course teaches practical implementation through:
1. Progressive complexity (foundations first)
2. Real-world project application
3. Performance-conscious coding
4. Best practices for web 3D

**Course URL**: https://threejs-journey.com/

---

## React Three Fiber (R3F) Ecosystem

### What is React Three Fiber?

React Three Fiber is a React renderer for Three.js. Instead of imperative WebGL commands, you write declarative React components that render into a WebGL context.

**GitHub**: https://github.com/pmndrs/react-three-fiber
**Documentation**: https://r3f.docs.pmnd.rs/

### Core Benefits

1. **Declarative Syntax**: Build scenes with JSX/React components
2. **Reusable Components**: Self-contained, composable 3D elements
3. **State Management**: React's state and props for 3D logic
4. **Ecosystem Integration**: Works with React libraries (animations, state, etc.)
5. **Performance**: React's scheduling outperforms imperative Three.js at scale

### R3F Ecosystem Libraries

#### Essential Libraries

**@react-three/drei**: Collection of helpers and abstractions
- Pre-built components and utilities
- Reduces boilerplate code
- Extensive helper functions for common patterns

**@react-three/postprocessing**: Easy post-processing effects
- Bloom, depth of field, motion blur
- Composable effect stack
- Performance-optimized

**@react-three/gltfjsx**: Converts GLTF models to JSX components
- Automatic model to component conversion
- Maintains material and animation data
- Simplifies model integration

#### Animation Libraries

- **React Spring**: Spring-physics animations for smooth motion
- **Framer Motion 3D**: Gesture and animation controls

#### State Management Solutions

- **Zustand**: Lightweight state management (recommended for R3F)
- **Jotai**: Atomic state approach
- **Valtio**: Proxy-based state

#### Physics Libraries

- **Rapier**: Advanced physics simulation
- **Jolt**: Physics engine with R3F support

#### UI Integration

- **Gooey UI**: UI elements within 3D scenes
- **UIKit**: Full UI solution for 3D applications

### Game Development with R3F

R3F is increasingly used for game development:
- First-class physics library support
- Active community for games
- Ecosystem continuously expanding for game-specific features
- Used in both enterprise applications and hobby game projects

### Should You Use R3F for Games?

**Advantages**:
- Declarative syntax improves code maintainability
- React ecosystem integration
- Component reusability
- Active development and community support
- Proven in production games

**Considerations**:
- Learning curve if unfamiliar with React
- Performance depends on proper optimization patterns
- Smaller ecosystem compared to traditional game engines

**Recommended**: Yes, especially for web-based games and interactive experiences

---

## Three.js Game Projects

### Examples of Three.js Games

#### Browser-Based Strategy Games

**Wardensity** (3D RTS)
- One of the first functional 3D RTS games in a browser
- Performance optimization: Merged draw calls from 600-1500 down to 30-50 per frame
- Technique: Massive draw call reduction through instancing and batching

**Resource Strategy Game**
- Age of Empires/Civilization-style gameplay
- Built with TypeScript
- GitHub: https://github.com/coloradude/resource-strategy-game

**Little-investor.io**
- RTS city-building IO game
- Showcase: https://discourse.threejs.org/t/little-investor-io-a-rts-city-building-io-game/16490

**Itch.io Strategy Games**:
Multiple notable games including Hollow Ground, FACEMINER, Zombies Per Minute, Might is Right, Buzzwords
- URL: https://itch.io/games/genre-strategy/made-with-threejs

#### Game Development Approaches

**Entity Component System (ECS) Pattern**
- TypeScript-based RTS engines use ECS for flexible game logic
- Separates concerns and improves maintainability
- Enables efficient state management

**GitHub Resources**:
- Three.js RTS ECS Engine: https://github.com/andvolodko/three.js-rts-ecs-engine
- RTS Game Implementation: https://github.com/emnh/rts

### Performance Techniques for Three.js Games

#### Draw Call Optimization
- **Instancing**: Key technique for reducing draw calls
  - InstancedMesh for rendering many identical objects in one call
  - Can render hundreds of thousands of objects with single draw call
  - Hundreds of objects per draw call is optimal (max ~1000)

#### Mobile Optimization
- Remove real-time lighting and shadows
- Use Matcap materials instead
- Significant performance improvement at cost of lighting quality

#### Large-Scale Rendering
- Cross-browser performance varies significantly
- Optimization requires testing and iteration

**Resources**:
- LogRocket Blog: https://blog.logrocket.com/creating-game-three-js/
- Building an RTS in Browser: https://46b.it/2021/built-an-rts-in-the-browser/

---

## AI-Assisted Three.js Workflows

### Overview

Developers increasingly use Claude, Copilot, and other AI tools to accelerate Three.js development, from shader generation to full scene creation.

### Practical AI Shader Workflow

#### Success Case: Shader Effect Gallery

One developer applied five different shader effects (wobble, wave, chromatic aberration, distortion, RGB split) to a full gallery page using AI-assisted generation:
- Time investment: Under 45 minutes total
- Per effect: 4 minutes from zero to working preview

**Techniques Used**:
- Claude Code for initial shader generation
- TSL (Three.js Shading Language) for WebGPU
- Interactive iteration and refinement

**Article**: https://www.mejba.me/blog/ai-shader-effects-claude-code

#### Key Workflows

**TSL Shader Generation with AI**
1. Provide reference documentation (eliminates ~90% of hallucinated errors)
2. Specify desired effect or behavior
3. AI generates working TSL code on first or second try
4. Iterate on parameters and visual output

**Common AI Shader Mistakes** (now avoidable with proper context):
- Deprecated imports
- Phantom functions that don't exist
- Compute shaders that compile but render nothing
- Result: Proper reference material can reduce errors dramatically

### Claude Skills for Three.js

#### Three.js WebGPU Skill

A Claude skill specifically designed for WebGPU and TSL development includes:
- Node materials patterns
- Compute shader templates
- Post-processing patterns
- WGSL integration examples
- Working code templates

**GitHub**: https://github.com/dgreenheck/webgpu-claude-skill

#### Three.js Skills Repository

Curated collection of modular skills for learning and development:
- Foundational lessons
- Ready-to-use examples
- Utilities for common patterns
- Shader templates
- Camera, lighting, material helpers

**GitHub**: https://github.com/CloudAI-X/threejs-skills

### AI for Full Project Generation

**Building React & Three.js Apps with AI**
- AI can assist in generating complete R3F scenes
- Shader effects from description
- Full gallery pages with effects
- Component structure assistance

**Articles**:
- Building React & Three.js Apps with Claude AI: https://www.arsturn.com/blog/ai-powered-development-building-react-threejs-apps-with-claude
- Getting AI to Write TSL That Works: https://threejsroadmap.com/blog/getting-ai-to-write-tsl-that-works

### AI Tools Comparison

- **Claude (with Code Interpreter)**: Excels at generating working TSL and shader code
- **ChatGPT**: Can generate shaders but may produce deprecated code
- **GitHub Copilot**: Good for boilerplate, less reliable for custom shaders

### Best Practices for AI-Assisted Three.js

1. Provide clear reference documentation (TSL reference, API docs)
2. Specify target (WebGPU/WebGL, GLSL/WGSL)
3. Include examples if available
4. Iterate on the generated code
5. Test thoroughly before production use

---

## Advanced Visual Techniques

### Physically-Based Rendering (PBR) and Realistic Materials

#### What is PBR?

Physically-Based Rendering simulates how light actually interacts with surfaces in the real world. It's the industry-standard method for both real-time and cinematic 3D.

#### Implementing PBR in Three.js

**Primary Material**: `MeshStandardMaterial`
- Industry-standard general-purpose material
- Should be your go-to for nearly all situations
- Supports full PBR workflow

**Essential Texture Maps**:
1. **Metalness Map** (blue channel):
   - Non-metallic (wood, stone): 0.0
   - Metallic: 1.0
   - Rusty metal: 0.0-1.0 range for partial metalness

2. **Roughness Map**:
   - 0.0 = smooth mirror reflection
   - 1.0 = fully diffuse, rough surface
   - Blended values for mixed surfaces

3. **Normal Map**:
   - RGB values affect surface normal per pixel
   - Changes how color is lit
   - Critical for surface detail

4. **Ambient Occlusion (AO) Map**:
   - Defines object's response to light
   - Creates softer, realistic shadows
   - Usually combined with base color

5. **Base Color Map**:
   - Fundamental surface color
   - Often combined with AO map in three.js

**Important**: In Three.js, combine AO, Roughness, and Metalness into one image where each component is accessed individually in shaders and mapped to control properties.

#### High-Quality Texture Resources

**3D Textures Library**: https://threejsresources.com/tool/3dtextures
- Free, high-quality PBR textures
- Covers metals, fabrics, stone, wood, etc.
- Essential resource for realistic surfaces

#### PBR Material Articles

- Experimenting with PBR Textures: https://medium.com/@Makoto_29712/experimenting-with-pbr-textures-usingthree-js-a25aad28ed65
- Understanding Material Types: https://moldstud.com/articles/p-understanding-material-types-in-threejs-a-comprehensive-guide-for-beginners
- Materials and PBR Documentation: https://threejsdemos.com/docs/materials
- Physically Based Rendering: https://discoverthreejs.com/book/first-steps/physically-based-rendering/

### Realistic Lighting with HDRI and Global Illumination

#### HDRI Environment Mapping

**What is HDRI?**
- High Dynamic Range Image
- Panoramic photo captured at multiple exposure levels
- Provides wider range of luminosity than standard images
- More detailed highlights and shadows

**Why HDRI?**
- Accurate illumination for realistic lighting
- Reflections on shiny surfaces
- Background that matches lighting
- Often better than traditional point lights

#### Implementation in Three.js

**Setup Process**:
1. Load HDR image using `RGBELoader`
2. Set as both background and environment map
3. Scene automatically lit from environment

**Three.js Features**:
- Supports RGBE (High Dynamic Range) Image-Based Lighting (IBL)
- Run-time generated pre-filtered roughness mipmaps (PMREM)
- Automatic cubemap generation from equirectangular images

**Best Practices**:
- Use high-resolution JPG/PNG for background
- Use smaller HDR for lighting and reflections
- Can use same image for both, but separate images often look better

#### Global Illumination Approaches

**Path Tracing**:
- Produces realistic global illumination
- Color bleeding between diffuse objects
- Refractive caustics from glass/water
- Three.js PathTracing Renderer: https://erichlof.github.io/THREE.js-PathTracing-Renderer/

**Real-time Results**: Achieves 60+ FPS with photorealistic global illumination

#### HDRI Resources

- Environment Maps: https://threejs-journey.com/lessons/environment-map
- HDR Lighting in Three.js: https://pixel-capture.com/tutorials/hdr-lighting-threejs-article
- Three.js Docs: https://threejs.org/docs/#api/en/scenes/Scene.environment

### Screen-Space Effects: SSAO, SSGI, Motion Blur, SSR

#### Screen Space Ambient Occlusion (SSAO)

**Purpose**: Creates depth and realism by darkening corners, crevices, and occluded areas

**Key Parameter**: N8AO - newer, faster, and better-looking alternative based on recent research

**Effect**: Most noticeable in corners and crevices where light is naturally blocked

#### Screen Space Global Illumination (SSGI)

**Capabilities**:
- Real-time color bleeding
- Dynamic emissive lighting
- Realistic light bounces in interactive scenes

**Quality**: Recent advances yield exceptional improvements in realism

**Half-Resolution Mode**:
- 2x-4x performance boost at quality cost
- Depth-aware upscaling adds ~1ms fixed cost

#### Motion Blur

**Implementation**:
- VelocityDepthNormalPass for tracking motion
- Per-object motion blur via velocity buffers
- Renders velocity from previous and current frames

**Use Case**: Cinematic camera movement, fast-moving objects

#### Temporal Anti-Aliasing (TRAA)

**Purpose**: Smooths jagged edges and improves image quality
- Uses temporal information from previous frames
- Better results than standard MSAA

#### The Realism Effects Library

Comprehensive library combining multiple effects:
- SSGI (Screen Space Global Illumination)
- SSAO
- Motion Blur
- TRAA
- Available in multiple variants

**GitHub**: https://github.com/0beqz/realism-effects
**Can be built with**: WebGPU, React Three Fiber, TSL

#### Forum Discussions and Resources

- SSGI Deep Dive: https://discourse.threejs.org/t/ssgi-screen-space-global-illumination/85190
- SSAO Examples: https://threejs.org/examples/webgl_postprocessing_ssao.html

### Volumetric Effects: Clouds, God Rays, Fog

#### Volumetric Clouds

**Two Approaches**:

1. **Game-Ready Volumetric Clouds**
   - Efficient implementation suitable for real-time rendering
   - Forum: https://discourse.threejs.org/t/volumetric-clouds-game-ready/86598

2. **Efficient Volumetric Clouds**
   - Research-based "Nubis, Evolved" implementation
   - Following Guerrilla Games work
   - Envelope Model approach
   - GitHub: https://github.com/FarazzShaikh/three-volumetric-clouds

**Technical Approach**:
- Ray marching: Shoot ray for each pixel going forward
- Pick samples along ray
- Shoot secondary rays toward light
- Compute light reaching observer

**Resource**: Three Volumetric Clouds: https://threejsresources.com/tool/three-volumetric-clouds

#### Volumetric Lighting (God Rays)

**Technique**: Similar to volumetric clouds but focuses on light rays through fog/particles

**Common Use Cases**: Atmospheric effects, light shafts through clouds, mystical atmosphere

#### Fog Systems

**Three.js Fog Types**:
- Linear fog
- Exponential fog
- Custom fog with post-processing

**Integration**: Works with all materials and post-processing effects

### Water and Ocean Rendering

#### Three.js Water Pro (Modern Approach)

**Technology**: Built with TSL and WebGPU

**Wave System**:
- Two-component wave system for ocean-quality results
- FFT-based simulation (Fast Fourier Transform)
  - Generates physically accurate ocean waves
  - Based on real oceanographic research
  - Produces wind-driven waves at every scale
- Gerstner swells
  - Large rolling open-ocean waves
  - Adds natural rolling motion

**Additional Features**:
- Dynamic Rayleigh sky model
- Volumetric clouds in demo app
- Real-time ocean simulation

**Documentation**: https://docs.threejswaterpro.com/
**Realistic Water Resources**: https://threejsresources.com/tool/three-js-water-pro

#### Ocean Shader (Traditional Approach)

**GitHub**: https://github.com/jbouny/ocean
- Realistic water shader for Three.js
- Works for complete ocean or small water surfaces
- Real-time simulation

### Realistic Space Visualization

#### Star Rendering

**Procedural Star Generation**:
- Attach custom vertex and fragment shaders to meshes
- Use 3D simplex noise for convection currents
- Base noise calculated at vertex coordinates
- Realistic stellar surface variation

**Article**: https://bpodgursky.com/2017/02/01/procedural-star-rendering-with-three-js-and-webgl-shaders/

#### Nebula Creation

**Two-Layer Approach**:
1. **Base Stars Layer**: Simple procedural noise-based stars
2. **Large Stars Layer**: Voronoi noise-based stars (larger)

**Animation**: Twinkling achieved through sinusoidal animation

**Nebulae Texture**:
- Based on fractal simplex noise
- Two distinct noise layers
- Final effect: Addition of both layers

#### Galaxy Simulation with WebGPU

**Advanced Technique**: Interactive spiral galaxies using:
- WebGPU compute shaders
- 1+ million stars rendered at 60 FPS
- Procedural star generation
- Dust clouds for depth

**Article**: https://threejsroadmap.com/blog/galaxy-simulation-webgpu-compute-shaders

#### Particle Systems for Space Effects

**Three Nebula**: WebGL-based 3D particle engine
- Designed for Three.js
- Alternative approach to procedural nebulae
- Full particle system control

**GitHub**: https://github.com/creativelifeform/three-nebula
**Website**: https://three-nebula.org/

#### NASA and Real Space Data

**NASA Projects Using Three.js**:
- Astromaterials 3D viewer: Interior CT data of rocks
- 3D Tiles Renderer: Mars terrain visualization for rover operations
- Real missions: Perseverance and Curiosity rovers
- Data visualization with real NASA data

**3D Tiles Renderer**: https://github.com/NASA-AMMOS/3DTilesRendererJS
- For representing 3D terrain and large datasets
- Context landscape and environment for rover operations

### Sci-Fi and Cyberpunk Visual Effects

#### Key Visual Elements

**SynthCity** (Infinite Procedural Cyberpunk City):
- Audiovisual experience combining web development and game development
- Procedural generation for infinite cityscape
- Sound design integration
- Cyberpunk aesthetics
- GitHub: https://github.com/joshstruve/synth-city-2179

**Sector 32 Portfolio**:
- Dark sci-fi interface
- Reflective chrome skull
- Cyan laser beams
- Retro terminal-style UI
- React Three Fiber implementation

#### Visual Effect Techniques

**Glitch Effects**: Digital artifact animation for cyberpunk aesthetic

**Shock Wave Animation**: Expanding energy waves with material distortion

**Flying Lines**: Tweened line animation for futuristic UI

**Radar Graphics**: Oscillating radial patterns with particle effects

**SMAA (Subpixel Morphological Antialiasing)**: Smooths jagged edges

**Bloom Effect Stacking**: Multiple layers of bloom for enhanced glow

#### Portal and Warp Effects

**3D Science Fiction Portal Effect**: Animated warp/portal visualization
- GitHub: https://github.com/sctlcd/threejs-sci-fi-portal-effect

### Cinematic Camera and Post-Processing

#### Tone Mapping for Cinematic Look

**Available Tone Mapping Options**:
- NoToneMapping
- LinearToneMapping
- ReinhardToneMapping
- CineonToneMapping (cinematic)
- ACESFilmicToneMapping (industry standard)

**Usage**: Set renderer's tone mapping and exposure to control light and color

**Cinematic Effect**: ACESFilmicToneMapping + adjusted exposure = professional cinematic look

#### Depth of Field

**Implementation**:
- Bokeh-based DOF with particle effects
- Blurry library generates millions of particles
- Particles randomly displaced in circle
- Distance from focal plane determines blur

**Practical Implementation**: https://threejs.org/examples/webgl_postprocessing_dof.html

#### Motion Blur

**Per-Frame Velocity Tracking**:
- Render velocity buffer from previous to current frame
- Smear final frame based on velocity
- Creates cinematic motion effect

**Library**: realism-effects offers MotionBlurEffect

### Post-Processing with EffectComposer

#### Overview

EffectComposer manages post-processing pipeline:
- RenderPass: Base rendering (must be first)
- Effect passes: Bloom, DOF, motion blur, etc.
- Final composition

#### Unreal Bloom Pass

**Key Parameters**:
- Resolution: Sharp results at cost of performance
- Strength: Intensity of glow (default 1.5)
- Radius: Area over which bloom spreads (default 0.4)
- Threshold: Brightness threshold for bloom (default 0.85)

**Technique**: Renders bright areas to separate texture, blurs, and composites back

**Example**: https://threejs.org/examples/webgl_postprocessing_unreal_bloom.html

---

## Performance Optimization Strategies

### Understanding Performance Constraints

The fundamental performance equation for Three.js:
- Total objects = what scene can render at 60 FPS
- Optimization determines what's possible
- Target: 16.67ms per frame at 60 FPS

### Draw Call Optimization

#### What is a Draw Call?

Each mesh is one draw call. CPU must communicate with GPU for each draw call.

**Optimal Range**:
- Maximum: ~1000 draw calls
- Ideal: Few hundred or less

#### Instancing Strategy

**InstancedMesh** is the primary technique for rendering many identical objects:

```
Technique: Single InstancedMesh with many instances = 1 draw call
Alternative: Separate meshes = N draw calls (where N = number of objects)
```

**Capabilities**:
- Render hundreds of thousands of objects in single draw call
- Only if meshes share same geometry and material

**Implementation Pattern**:
- Create geometry once
- Create material once
- Create InstancedMesh with count
- Set position/rotation/scale per instance via attributes

**Advanced**: GPU-based culling with compute shaders for per-frame instance selection

#### Geometry Merging

Combine multiple geometries into single mesh (when not using instancing):
- Reduces draw calls
- Less flexible than instancing
- Good for static geometry

### Level of Detail (LOD)

#### What is LOD?

Adjust object complexity based on distance from camera:
- Close objects: High polygon count
- Distant objects: Lower polygon count
- Dramatic performance improvement

#### When LOD Helps

- Scenes with many objects
- Large viewing distances
- Models with high polygon counts

#### How LOD Works

1. Measure distance between camera and object
2. Select appropriate detail level
3. Swap geometry based on distance threshold
4. Reduces vertex count = GPU work reduction

#### Advanced: GPU-Based LOD

- Compute shaders can perform LOD selection on GPU
- Frustum culling also on GPU
- Essential for rendering millions of instances

**Resources**:
- Enhancing Three.js Performance with LOD: https://waelyasmina.net/articles/enhancing-three-js-app-performance-with-lod/
- When LOD is Beneficial: https://discourse.threejs.org/t/when-is-it-actually-beneficial-to-use-lod-in-three-js-for-performance/87697

### Frustum Culling and Visibility Management

#### What is Frustum Culling?

Don't render objects outside camera's view (frustum)
- Invisible objects take 0 GPU time
- Automatic for individual meshes
- Must implement manually for InstancedMesh

#### Implementing Frustum Culling

**For InstancedMesh**:
1. Divide world into regions/cells
2. Cull regions outside frustum
3. Only render instances in visible regions
4. Prevents whole mesh from being rendered if all instances are off-screen

**Advanced Approach**: Per-instance culling on GPU with compute shaders

**Forum Discussion**: https://discourse.threejs.org/t/ideas-on-performing-fast-per-instance-frustum-culling-on-instancedmesh/85156

#### Selective Shadows

Only cast shadows from visible objects:
- Reduces shadow map updates
- Significant performance gain
- Maintained visual quality

### Memory Management

#### Critical Issue: Three.js Doesn't Auto-Cleanup

You must manually track and dispose:
- Geometries
- Textures
- Materials
- Other resources

**Pattern**:
```javascript
// Track created resources
const resources = [];

// When done
resources.forEach(resource => resource.dispose());
```

**Best Practice**: Use IntersectionObserver to detect viewport visibility
- Only load/render when visible
- Unload when not visible
- Automatic memory management

### Shader Optimization

#### GLSL vs TSL vs WGSL

**Traditional GLSL**:
- Mature, widely supported
- Manual optimization required
- Vendor-specific performance variations

**TSL (Three.js Shading Language)**:
- JavaScript-based shader language
- Compiles to both GLSL (WebGL) and WGSL (WebGPU)
- Automatic optimization:
  - Temporary variables for repeated expressions
  - Uniform reuse
  - Dead code elimination

**Key Advantage**: Write once, runs on both WebGL and WebGPU

#### Performance Optimization Techniques

**Automatic TSL Optimizations**:
- Compiler knows when to multiply by model matrix
- Declares uniform once, not multiple times
- Eliminates dead code automatically

**Debugging**: TSL provides JavaScript stack traces instead of cryptic GLSL errors

#### Migration Complexity

- Simple projects (standard materials): 1-2 hours
- Projects with custom GLSL: 1-2 days for TSL conversion
- Large applications with complex post-processing: 1-2 weeks

**Resources**:
- Why TSL is Important: https://discourse.threejs.org/t/why-tsl-three-js-shading-language-is-so-interesting/56306
- TSL: A Better Way to Write Shaders: https://threejsroadmap.com/blog/tsl-a-better-way-to-write-shaders-in-threejs
- Field Guide to TSL and WebGPU: https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/
- WebGL vs WebGPU: https://threejsroadmap.com/blog/webgl-vs-webgpu-explained

### Texture Optimization

#### Texture Compression Formats

**PNG vs WebP vs KTX2**:
- PNG: Uncompressed, large file size
- WebP: 25-35% smaller than PNG/JPEG, modern support
- KTX2 with Basis Universal: Massive bandwidth and VRAM savings

**Case Study**:
- Swapping 2048x2048 PNG to 1024x1024 WebP
- Result: 40% memory reduction
- Quality impact: Negligible on mid-tier smartphones

**Advanced**: ASTC and ETC2 compression with KTX container
- Dramatic bandwidth savings
- Performance dependent on target GPU support

#### When to Use Each Format

**First Contentful Paint (FCP) Optimization**:
- Minimize file size with WebP or AVIF
- Smaller downloads = faster initial load

**VRAM Efficiency**:
- KTX2 is best for runtime memory efficiency
- Especially important for mobile

**Recommendation**:
- Use WebP for web delivery (balance of quality and size)
- Use KTX2 for long-session apps with many textures

**Resources**:
- Choosing Texture Formats: https://www.donmccurdy.com/2024/02/11/web-texture-formats/
- Top Texture Optimization Techniques: https://moldstud.com/articles/p-top-texture-optimization-techniques-for-boosting-threejs-application-performance
- Compressed Texture Workflow: https://discourse.threejs.org/t/compressed-texture-workflow-gltf-basis/10039

### Production Performance Case Studies

#### Wardensity RTS Optimization

**Problem**: Initial performance: 600-1500 draw calls per frame

**Solution**: Aggressive draw call merging

**Result**: 30-50 draw calls per frame (50-98% reduction)

**Technique**: Merging compatible meshes and using instancing

#### Advanced Production Techniques

**100 Three.js Tips for Performance** (2026):
https://www.utsubo.com/blog/threejs-best-practices-100-tips

**React Three Fiber Scaling**:
https://r3f.docs.pmnd.rs/advanced/scaling-performance

---

## Specific Implementation Deep-Dives

### Blender to Three.js Workflow

#### Overview

Modern workflow for creating high-quality 3D content:
1. Create and design in Blender
2. Bake lighting and effects
3. Export to glTF 2.0 format
4. Load and display in Three.js

#### Model Preparation

**Constraints**:
- Low to middle polygon count (200k triangles for smooth 60 FPS)
- Single Principled BSDF node per material (glTF requirement)
- Limited texture support

**Supported Texture Maps**:
- Color (Diffuse)
- Metallic
- Roughness
- Ambient Occlusion (AO)
- Normal Map
- Emissive

**Unsupported**: Displacement maps (use normal maps instead)

#### Baking Technique

**What is Baking?**
Rendering the scene onto UV coordinates of models

**Common Baking Targets**:
- Full lit scene
- Individual render channels
- Normal maps
- Ambient occlusion
- Emissive maps

**Benefit**: Save complex lighting calculations into texture maps
- Real-time rendering just applies texture
- Dramatic performance improvement

**Implementation**:
1. Set up lighting in Blender
2. Configure bake target texture
3. Bake in Bake tab
4. Export with material

#### Export Process

**Steps**:
1. Enable glTF 2.0 addon (Preferences > Add-ons > glTF 2.0)
2. File > Export > glTF 2.0 (.glb/.gltf)
3. Configure export settings
4. Export to project

**File Formats**:
- .glb: Binary format (recommended, smaller file)
- .gltf: ASCII format with separate assets

#### Texture Optimization

**Modern Recommendations**:
- KTX2 or WebP formats
- Smaller file sizes, better quality
- Properly compressed

**Typical Setup**:
- High-quality master textures in Blender
- Export to glTF with standard formats
- Convert to KTX2/WebP using tool like TextureCompressor

#### Resources

- Making 3D Web Apps with Blender and Three.js: https://www.soft8soft.com/wiki/index.php/Making_3D_web_apps_with_Blender_and_Three.js
- Building a Fully-Featured 3D World: https://tympanus.net/codrops/2025/04/08/3d-world-in-the-browser-with-blender-and-three-js/
- Three.js Baking Guide: https://codepen.io/alaingalvan/post/guide-three-js-baking
- Baking and Exporting: https://threejs-journey.com/lessons/baking-and-exporting-the-scene
- Blender to Three.js Export Guide: https://github.com/funwithtriangles/blender-to-threejs-export-guide

### Advanced Animation Techniques

#### Scroll-Based Animation

**Pattern**: Three.js scene responds to page scroll

**Implementation**:
- Listen to scroll events
- Update camera/object positions based on scroll
- Sync animations with page content

**Advanced**: Infinite looping scroll with shaders

**Resource**: https://tympanus.net/codrops/2022/01/05/crafting-scroll-based-animations-in-three-js/

#### Physics-Based Particles

**Technique**: Drop voxelized video pixels into physics world

**Libraries**: Three.js + Rapier physics engine

**Result**: Stunning visual effect of video content transforming into physics-driven particles

### Advanced Color and Tone Management

#### Color Space Handling

**Critical**: Renderer must work with original image colors for accurate calculations

**Process**:
1. Load images in original color space
2. Perform calculations
3. Apply gamma correction (sRGB encoding)

**Result**: Accurate lighting and realistic appearance

#### Bump and Surface Details

**Maps Used**:
- Bump maps: Height information (simpler than normal maps)
- Normal maps: Per-pixel surface direction (more detailed)
- Roughness maps: Surface finish variation

### Interactive Raycasting

**Technique**: Detect mouse clicks on 3D objects

**Implementation**:
1. Create Raycaster
2. On mouse move/click, cast ray from camera through mouse position
3. Check intersections with scene objects
4. Trigger interactions on hit objects

**Use Cases**: Clickable 3D UI elements, object selection, hover effects

**Resource**: Bruno Simon's course covers this in detail

---

## Conclusion

The Three.js ecosystem has evolved into a mature platform for creating exceptional 3D web experiences. The most impressive visual showcases combine:

1. **Technical Foundation**: PBR materials, HDRI lighting, efficient geometry management
2. **Advanced Rendering**: Screen-space effects, volumetric systems, post-processing
3. **Smart Optimization**: Instancing, LOD, draw call merging, texture compression
4. **Creative Vision**: Artistic use of effects, color grading, atmosphere

The combination of:
- Powerful tools (Bruno Simon's course, R3F ecosystem, Codrops tutorials)
- AI-assisted development (Claude, Copilot)
- Community knowledge (GitHub, forums, articles)
- Proven optimization techniques

...makes it possible for developers to create photorealistic, performant, and visually stunning 3D web experiences.

---

## Quick Reference: Key Resources by Category

### Learning
- **Bruno Simon's Three.js Journey**: https://threejs-journey.com/
- **Codrops Tutorials**: https://tympanus.net/codrops/tag/three-js/
- **Discover Three.js**: https://discoverthreejs.com/

### Inspiration
- **Awwwards Three.js**: https://www.awwwards.com/websites/three-js/
- **The FWA**: https://thefwa.com/
- **Three.js Resources**: https://threejsresources.com/

### Development
- **React Three Fiber**: https://r3f.docs.pmnd.rs/
- **Three.js Documentation**: https://threejs.org/docs/
- **Three.js Forum**: https://discourse.threejs.org/

### Optimization
- **100 Three.js Tips**: https://www.utsubo.com/blog/threejs-best-practices-100-tips
- **Scaling Performance with R3F**: https://r3f.docs.pmnd.rs/advanced/scaling-performance
- **Realism Effects Library**: https://github.com/0beqz/realism-effects

### Assets and Tools
- **3D Textures**: https://threejsresources.com/tool/3dtextures
- **Three.js Water Pro**: https://docs.threejswaterpro.com/
- **Texture Compressor**: https://github.com/TimvanScherpenzeel/texture-compressor

### AI-Assisted Development
- **Claude Code for Three.js**: https://www.arsturn.com/blog/ai-powered-development-building-react-threejs-apps-with-claude
- **Three.js Skills**: https://github.com/CloudAI-X/threejs-skills
- **TSL Writing Guide**: https://threejsroadmap.com/blog/getting-ai-to-write-tsl-that-works
