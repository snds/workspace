# Gameplay Programming: Core Systems for Legion (TypeScript/Three.js)

Implementation patterns for Legion's pillars: factory simulation, resource management, RTS combat, AI, exploration, input handling, and camera systems.

## Factory Simulation: Tick-Based Production

Legion's core gameplay loop is **production chains**: extract ore, refine it, manufacture components, assemble final products.

### Production Component (Tick-Based)

```typescript
class ProductionComponent extends Component {
  private rate: number; // units per second
  private accumulatedOutput: number = 0;
  private isProducing: boolean = false;
  private inputRequirements: { [resource: string]: number } = {};
  private outputResource: string = "";

  onItemProduced = new EventEmitter<{ resource: string; amount: number }>();

  constructor(config: {
    rate: number;
    inputs: { [resource: string]: number };
    output: string;
  }) {
    super();
    this.rate = config.rate;
    this.inputRequirements = config.inputs;
    this.outputResource = config.output;
  }

  update(deltaTime: number): void {
    if (!this.isProducing || !this.canProduce()) {
      this.isProducing = false;
      return;
    }

    // Accumulate production
    this.accumulatedOutput += this.rate * deltaTime;

    // Emit complete items
    while (this.accumulatedOutput >= 1.0) {
      this.onItemProduced.emit({
        resource: this.outputResource,
        amount: 1
      });
      this.accumulatedOutput -= 1.0;

      // Consume inputs
      const storage = this.entity!.getComponent(StorageComponent);
      if (storage) {
        for (const [resource, amount] of Object.entries(this.inputRequirements)) {
          storage.removeResource(resource, amount);
        }
      }
    }
  }

  private canProduce(): boolean {
    const storage = this.entity!.getComponent(StorageComponent);
    if (!storage) return false;

    // Check if we have enough inputs
    for (const [resource, required] of Object.entries(this.inputRequirements)) {
      if (!storage.hasEnough(resource, required)) {
        return false;
      }
    }

    return true;
  }

  startProduction(): void {
    this.isProducing = true;
  }

  stopProduction(): void {
    this.isProducing = false;
  }
}
```

### Conveyor System

Resources flow between buildings via conveyor belt simulation:

```typescript
class ConveyorBelt {
  source: Entity;
  destination: Entity;
  transferRate: number = 5; // units per second
  resourceType: string = "";
  mesh: THREE.Mesh;

  constructor(
    source: Entity,
    dest: Entity,
    resourceType: string,
    rate: number
  ) {
    this.source = source;
    this.destination = dest;
    this.resourceType = resourceType;
    this.transferRate = rate;

    // Create visual conveyor mesh
    const sourcePos = source.position;
    const destPos = dest.position;

    const distance = sourcePos.distanceTo(destPos);
    const geometry = new THREE.BoxGeometry(10, 5, distance);
    const material = new THREE.MeshStandardMaterial({ color: 0x444444 });

    this.mesh = new THREE.Mesh(geometry, material);

    // Position between source and destination
    this.mesh.position.copy(sourcePos.clone().add(destPos).multiplyScalar(0.5));
    this.mesh.lookAt(destPos);
  }

  update(deltaTime: number): void {
    const amount = this.transferRate * deltaTime;

    const sourceStorage = this.source.getComponent(StorageComponent);
    const destStorage = this.destination.getComponent(StorageComponent);

    if (sourceStorage && destStorage) {
      const removed = sourceStorage.removeResource(this.resourceType, amount);
      destStorage.addResource(this.resourceType, removed);
    }
  }
}

class ConveyorManager {
  private conveyors: ConveyorBelt[] = [];

  addConveyor(
    source: Entity,
    dest: Entity,
    resourceType: string,
    rate: number
  ): ConveyorBelt {
    const belt = new ConveyorBelt(source, dest, resourceType, rate);
    this.conveyors.push(belt);
    return belt;
  }

  update(deltaTime: number): void {
    for (const belt of this.conveyors) {
      belt.update(deltaTime);
    }
  }
}
```

## Resource Management System

Resources are the lifeblood of Legion's economy: ore, metals, components, energy.

```typescript
class StorageComponent extends Component {
  private inventory: Map<string, number> = new Map();
  private capacity: Map<string, number> = new Map();

  onInventoryChanged = new EventEmitter<{ resource: string; amount: number }>();

  constructor(capacities: { [resource: string]: number }) {
    super();
    for (const [resource, cap] of Object.entries(capacities)) {
      this.inventory.set(resource, 0);
      this.capacity.set(resource, cap);
    }
  }

  addResource(resourceType: string, amount: number): number {
    const current = this.inventory.get(resourceType) ?? 0;
    const max = this.capacity.get(resourceType) ?? 1000;

    const added = Math.min(amount, max - current);
    this.inventory.set(resourceType, current + added);

    if (added > 0) {
      this.onInventoryChanged.emit({ resource: resourceType, amount: added });
    }

    return added;
  }

  removeResource(resourceType: string, amount: number): number {
    const current = this.inventory.get(resourceType) ?? 0;
    const removed = Math.min(amount, current);
    this.inventory.set(resourceType, current - removed);

    if (removed > 0) {
      this.onInventoryChanged.emit({ resource: resourceType, amount: -removed });
    }

    return removed;
  }

  hasEnough(resourceType: string, amount: number): boolean {
    const current = this.inventory.get(resourceType) ?? 0;
    return current >= amount;
  }

  getAmount(resourceType: string): number {
    return this.inventory.get(resourceType) ?? 0;
  }

  update(deltaTime: number): void {
    // Storage is passive
  }
}
```

## RTS Combat Systems

Real-time strategy: select units, give commands, watch formations engage enemies.

### Unit Selection with Raycasting

```typescript
class CombatController {
  private selectedUnits: Set<Unit> = new Set();
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2();
  private selectionBox = new THREE.Box3();

  constructor(camera: THREE.Camera, scene: THREE.Scene) {
    document.addEventListener("click", (event) => {
      this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

      this.raycaster.setFromCamera(this.mouse, camera);

      // Find units under cursor
      const units: any[] = [];
      scene.traverse((obj) => {
        if ((obj as any).isUnit) units.push(obj);
      });

      const intersects = this.raycaster.intersectObjects(units);

      if (!event.ctrlKey) {
        this.selectedUnits.clear();
      }

      if (intersects.length > 0) {
        const selectedUnit = intersects[0].object;
        if ((selectedUnit as any).unit) {
          this.selectedUnits.add((selectedUnit as any).unit);
          (selectedUnit as any).unit.select();
        }
      }
    });
  }

  moveSelectedUnits(targetPos: THREE.Vector3): void {
    for (const unit of this.selectedUnits) {
      unit.moveTo(targetPos);
    }
  }

  attackSelectedUnits(targetUnit: Unit): void {
    for (const unit of this.selectedUnits) {
      unit.attack(targetUnit);
    }
  }
}
```

### Unit Movement & Pathfinding

```typescript
import { Pathfinding } from "three-pathfinding";

class Unit extends Component {
  private pathfinding: Pathfinding | null = null;
  private path: THREE.Vector3[] = [];
  private pathIndex: number = 0;
  private velocity: THREE.Vector3 = new THREE.Vector3();
  private speed: number = 100; // units per second

  moveTo(targetPosition: THREE.Vector3): void {
    // Simple A* pathfinding (or use a library)
    // For now, just move directly
    this.path = [targetPosition];
    this.pathIndex = 0;
  }

  update(deltaTime: number): void {
    if (this.path.length === 0) return;

    const target = this.path[this.pathIndex];
    const direction = target.clone().sub(this.entity!.position).normalize();

    // Move toward target
    this.entity!.position.addScaledVector(direction, this.speed * deltaTime);

    // Check if reached waypoint
    if (this.entity!.position.distanceTo(target) < 10) {
      this.pathIndex++;
      if (this.pathIndex >= this.path.length) {
        this.path = [];
      }
    }
  }

  attack(targetUnit: Unit): void {
    // Move close to target
    const targetPos = targetUnit.entity!.position.clone();
    const direction = targetPos.sub(this.entity!.position).normalize();
    targetPos.addScaledVector(direction, -200); // Stop 200 units away

    this.moveTo(targetPos);

    // Fire weapons (in a real game, track target and fire)
    // This is simplified
  }

  select(): void {
    // Visual feedback
    const highlight = new THREE.PointLight(0x00ff00, 1, 100);
    this.entity!.add(highlight);
  }

  deselect(): void {
    // Remove visual feedback
    this.entity!.children = this.entity!.children.filter(
      (c) => !(c instanceof THREE.Light)
    );
  }
}
```

### Formation Movement

```typescript
class Formation {
  private units: Unit[] = [];
  private formationType: "line" | "square" | "wedge" = "line";
  private spacing: number = 200;

  addUnit(unit: Unit): void {
    this.units.push(unit);
  }

  moveTo(destination: THREE.Vector3): void {
    const positions = this.calculateFormationPositions(destination);

    for (let i = 0; i < this.units.length; i++) {
      if (positions[i]) {
        this.units[i].moveTo(positions[i]);
      }
    }
  }

  private calculateFormationPositions(center: THREE.Vector3): THREE.Vector3[] {
    const positions: THREE.Vector3[] = [];

    switch (this.formationType) {
      case "line":
        for (let i = 0; i < this.units.length; i++) {
          positions.push(
            center.clone().addScaledVector(new THREE.Vector3(1, 0, 0), i * this.spacing)
          );
        }
        break;

      case "square":
        const gridSize = Math.ceil(Math.sqrt(this.units.length));
        for (let i = 0; i < this.units.length; i++) {
          const x = (i % gridSize) * this.spacing;
          const z = Math.floor(i / gridSize) * this.spacing;
          positions.push(center.clone().add(new THREE.Vector3(x, 0, z)));
        }
        break;

      case "wedge":
        for (let i = 0; i < this.units.length; i++) {
          const x = (i % 3) * this.spacing;
          const z = Math.floor(i / 3) * this.spacing;
          positions.push(center.clone().add(new THREE.Vector3(x - this.spacing, 0, z)));
        }
        break;
    }

    return positions;
  }
}
```

### Fog of War

```typescript
class FogOfWarManager {
  private exploredCells: Set<string> = new Set();
  private revealRadius: number = 1000;
  private gridSize: number = 100;
  private cellSize: number = 100;

  revealAroundUnit(unit: Unit): void {
    const pos = unit.entity!.position;

    for (let x = 0; x < this.gridSize; x++) {
      for (let z = 0; z < this.gridSize; z++) {
        const cellCenter = new THREE.Vector3(x * this.cellSize, 0, z * this.cellSize);
        if (pos.distanceTo(cellCenter) <= this.revealRadius) {
          const key = `${x},${z}`;
          this.exploredCells.add(key);
        }
      }
    }
  }

  isCellExplored(x: number, z: number): boolean {
    return this.exploredCells.has(`${x},${z}`);
  }

  updateAllUnits(units: Unit[]): void {
    for (const unit of units) {
      this.revealAroundUnit(unit);
    }
  }
}
```

## AI for NPCs & Threats

**Behavior Trees** orchestrate NPC actions.

```typescript
interface BehaviorTreeNode {
  execute(entity: Entity): "success" | "failure" | "running";
}

class SelectorNode implements BehaviorTreeNode {
  private children: BehaviorTreeNode[] = [];

  addChild(node: BehaviorTreeNode): void {
    this.children.push(node);
  }

  execute(entity: Entity): "success" | "failure" | "running" {
    for (const child of this.children) {
      const result = child.execute(entity);
      if (result !== "failure") {
        return result;
      }
    }
    return "failure";
  }
}

class SequenceNode implements BehaviorTreeNode {
  private children: BehaviorTreeNode[] = [];

  addChild(node: BehaviorTreeNode): void {
    this.children.push(node);
  }

  execute(entity: Entity): "success" | "failure" | "running" {
    for (const child of this.children) {
      const result = child.execute(entity);
      if (result !== "success") {
        return result;
      }
    }
    return "success";
  }
}

class IsUnderAttackNode implements BehaviorTreeNode {
  execute(entity: Entity): "success" | "failure" {
    const health = entity.getComponent(HealthComponent);
    if (health && health.isDamaged()) {
      return "success";
    }
    return "failure";
  }
}

class CombatBehaviorNode implements BehaviorTreeNode {
  execute(entity: Entity): "success" | "failure" {
    // Chase enemy, attack, etc.
    console.log("Entering combat");
    return "success";
  }
}

// Build behavior tree
const root = new SelectorNode();
const isUnderAttack = new IsUnderAttackNode();
const combatBehavior = new CombatBehaviorNode();

root.addChild(isUnderAttack);
root.addChild(combatBehavior);

// Execute in game loop
function updateAI(entity: Entity): void {
  root.execute(entity);
}
```

### Utility AI Scoring

```typescript
class UtilityAI {
  private alertness: number = 0;

  update(deltaTime: number, enemyInSight: boolean): "patrol" | "combat" {
    // Update alertness
    this.alertness = enemyInSight ? 1.0 : Math.max(0, this.alertness - deltaTime);

    const patrolScore = this.scorePatrol();
    const combatScore = this.scoreCombat();

    return combatScore > patrolScore ? "combat" : "patrol";
  }

  private scorePatrol(): number {
    // Patrol is good when relaxed
    return 1.0 - this.alertness;
  }

  private scoreCombat(): number {
    // Combat is good when there's a threat
    return this.alertness;
  }
}
```

## Exploration Mechanics

**Scanning** reveals resource deposits and points of interest.

```typescript
class ScanComponent extends Component {
  private scanRange: number = 5000;
  private scanDuration: number = 3.0;
  private scanProgress: number = 0;
  private isScanning: boolean = false;

  onScanStarted = new EventEmitter<void>();
  onScanCompleted = new EventEmitter<void>();
  onAsteroidDiscovered = new EventEmitter<{ position: THREE.Vector3; resources: string[] }>();

  startScan(): void {
    this.isScanning = true;
    this.scanProgress = 0;
    this.onScanStarted.emit();
  }

  update(deltaTime: number): void {
    if (!this.isScanning) return;

    this.scanProgress += deltaTime / this.scanDuration;

    if (this.scanProgress >= 1.0) {
      this.completeScan();
      this.isScanning = false;
    }
  }

  private completeScan(): void {
    const pos = this.entity!.position;

    // Find nearby asteroids
    for (let i = 0; i < 20; i++) {
      const angle = (Math.random() * Math.PI * 2);
      const distance = Math.random() * this.scanRange;
      const asteroidPos = new THREE.Vector3(
        pos.x + Math.cos(angle) * distance,
        Math.random() * 5000,
        pos.z + Math.sin(angle) * distance
      );

      this.onAsteroidDiscovered.emit({
        position: asteroidPos,
        resources: ["iron", "copper"]
      });
    }

    this.onScanCompleted.emit();
  }
}
```

## Input Handling: Multi-Mode Gameplay

Legion has three modes: Building, Combat, Exploration. Input context shifts.

```typescript
enum GameMode {
  Building = "building",
  Combat = "combat",
  Exploration = "exploration"
}

class InputManager {
  private currentMode: GameMode = GameMode.Exploration;
  private bindings: Map<string, (key: string) => void> = new Map();

  constructor() {
    document.addEventListener("keydown", (event) => {
      const handler = this.bindings.get(`${this.currentMode}:${event.key}`);
      if (handler) handler(event.key);
    });
  }

  setMode(mode: GameMode): void {
    this.currentMode = mode;
    console.log(`Switched to ${mode} mode`);
  }

  bindKey(mode: GameMode, key: string, handler: () => void): void {
    this.bindings.set(`${mode}:${key}`, handler);
  }
}

// Usage
const input = new InputManager();

input.bindKey(GameMode.Building, "q", () => {
  console.log("Rotating building");
});

input.bindKey(GameMode.Combat, "a", () => {
  console.log("Attacking");
});
```

## Camera Systems

Support strategic overview, close inspection, and unit following:

```typescript
class CameraController {
  private camera: THREE.PerspectiveCamera;
  private targetPosition: THREE.Vector3 = new THREE.Vector3();
  private currentDistance: number = 5000;
  private targetDistance: number = 5000;

  private strategicDistance: number = 5000;
  private inspectionDistance: number = 500;
  private unitFollowDistance: number = 800;

  constructor(camera: THREE.PerspectiveCamera) {
    this.camera = camera;
  }

  focusOnBuilding(building: Entity): void {
    this.targetPosition = building.position.clone();
    this.targetDistance = this.inspectionDistance;
  }

  followUnit(unit: Unit): void {
    this.targetPosition = unit.entity!.position.clone();
    this.targetDistance = this.unitFollowDistance;
  }

  returnToOverview(): void {
    this.targetPosition = new THREE.Vector3(0, 0, 0);
    this.targetDistance = this.strategicDistance;
  }

  update(deltaTime: number): void {
    // Smooth camera movement
    const direction = this.targetPosition.clone().sub(this.camera.position).normalize();
    this.camera.position.addScaledVector(direction, 500 * deltaTime);

    // Smooth zoom
    this.currentDistance = this.lerp(this.currentDistance, this.targetDistance, deltaTime * 2);

    // Update camera position to look down at the world
    const height = this.currentDistance * Math.sin(Math.PI / 6); // 30 degree angle
    const horizontal = this.currentDistance * Math.cos(Math.PI / 6);

    this.camera.position.set(
      this.targetPosition.x + horizontal,
      height,
      this.targetPosition.z + horizontal
    );

    this.camera.lookAt(this.targetPosition);
  }

  private lerp(a: number, b: number, t: number): number {
    return a + (b - a) * t;
  }
}
```

---

**These systems form the core gameplay loop: extract resources, manage production, build armies, explore the galaxy. Every system broadcasts events so UI, audio, and analytics can respond independently.**
