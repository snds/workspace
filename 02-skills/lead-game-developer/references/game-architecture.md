# Game Architecture Patterns for Legion (Three.js/TypeScript)

How to structure Legion for the web so it scales from prototype to shipping title, remains flexible for designers and artists, and performs well on target devices.

## Project Structure: Folder Conventions

A Three.js game needs clear organization. Here's the Legion structure:

```
legion-game/
├── src/
│   ├── core/               # Engine-agnostic game logic
│   │   ├── entities/       # Entity and component base classes
│   │   ├── components/     # Reusable component classes
│   │   ├── systems/        # Game systems (managers)
│   │   ├── events/         # Event emitter and bus
│   │   └── state/          # State machine implementations
│   ├── scenes/             # Three.js scenes (Factory, Combat, Exploration)
│   ├── config/             # JSON config files (balance, difficulty)
│   ├── data/               # Procedural generation, seeded data
│   ├── input/              # Input handling (keyboard, mouse, touch)
│   ├── camera/             # Camera controllers
│   ├── audio/              # Sound effects and music
│   ├── ui/                 # HUD and menu UI
│   ├── save/               # Save/load logic (IndexedDB)
│   ├── loader/             # Asset loading (textures, meshes, models)
│   └── main.ts             # Application entry point
├── public/
│   ├── assets/             # 3D models, textures, audio
│   │   ├── models/
│   │   ├── textures/
│   │   └── audio/
│   └── index.html
├── config/
│   ├── production_rates.json
│   ├── difficulty.json
│   ├── units.json
│   └── buildings.json
├── tests/                  # Unit and integration tests
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
└── package.json
```

**Why this structure?**
- **core/** houses reusable systems decoupled from scenes
- **scenes/** keeps scene-specific setup together
- **config/** isolates balance data (designers edit JSON)
- Clear separation enables parallel work: artists in assets while designers tune config
- **loader/** centralizes asset management (pooling, caching)

## Entity-Component Architecture in TypeScript

Like design system components—but for game objects in the world.

### The Entity/Component Model

An **Entity** is a container. A **Component** is a chunk of data or behavior. Entities own Components; Components don't own each other.

Example: **Factory Building Entity** composed of:

```typescript
class Entity {
  id: string;
  components: Map<string, Component> = new Map();

  addComponent<T extends Component>(component: T): T {
    this.components.set(component.constructor.name, component);
    return component;
  }

  getComponent<T extends Component>(type: new (...args: any[]) => T): T | undefined {
    return this.components.get(type.name) as T;
  }
}

// Example composition:
const factoryBuilding = new Entity("factory_1");
factoryBuilding.addComponent(new TransformComponent(100, 200, 50));
factoryBuilding.addComponent(new ProductionComponent({ rate: 10 }));
factoryBuilding.addComponent(new StorageComponent({ capacity: 1000 }));
factoryBuilding.addComponent(new HealthComponent({ hp: 100 }));
factoryBuilding.addComponent(new UIComponent()); // Renders health bar, UI
```

Each component is **independent**: Production doesn't know about Storage; Health doesn't care about Power consumption. They all broadcast events.

### Creating a Component

```typescript
abstract class Component {
  entity: Entity | null = null;

  abstract update(deltaTime: number): void;
}

class ProductionComponent extends Component {
  rate: number = 10; // units per second
  accumulatedOutput: number = 0;
  isProducing: boolean = false;

  onItemProduced = new EventEmitter<{ item: string; amount: number }>();

  update(deltaTime: number): void {
    if (!this.isProducing) return;

    this.accumulatedOutput += this.rate * deltaTime;

    while (this.accumulatedOutput >= 1.0) {
      this.onItemProduced.emit({ item: "iron", amount: 1 });
      this.accumulatedOutput -= 1.0;
    }
  }

  startProduction(): void {
    this.isProducing = true;
  }

  stopProduction(): void {
    this.isProducing = false;
  }
}

class StorageComponent extends Component {
  inventory: Map<string, number> = new Map();
  capacity: Map<string, number> = new Map();

  onInventoryChanged = new EventEmitter<{ resource: string; amount: number }>();

  addResource(resourceType: string, amount: number): boolean {
    const current = this.inventory.get(resourceType) ?? 0;
    const max = this.capacity.get(resourceType) ?? 1000;

    if (current + amount <= max) {
      this.inventory.set(resourceType, current + amount);
      this.onInventoryChanged.emit({ resource: resourceType, amount });
      return true;
    }
    return false;
  }

  removeResource(resourceType: string, amount: number): number {
    const current = this.inventory.get(resourceType) ?? 0;
    const removed = Math.min(amount, current);
    this.inventory.set(resourceType, current - removed);
    return removed;
  }

  update(deltaTime: number): void {}
}
```

**Why composition over inheritance?**
- Inheritance creates brittle hierarchies ("Is a Factory a Building? Is a mobile factory?")
- Composition is flexible: swap Production for Mining, add Defense—all by composing components
- Mirrors design systems: Button is never a subclass of Heading; both are independent components

## State Management Patterns

Games are state machines: menus, gameplay, paused, game-over. Legion needs clean transitions.

### Finite State Machines (FSMs)

A Building has states: Idle, Producing, PoweredOff, Damaged, Destroyed.

```typescript
enum BuildingState {
  Idle = "idle",
  Producing = "producing",
  PoweredOff = "powered_off",
  Damaged = "damaged",
  Destroyed = "destroyed"
}

class BuildingStateMachine {
  private currentState: BuildingState = BuildingState.Idle;
  private entity: Entity;

  onStateChanged = new EventEmitter<{ from: BuildingState; to: BuildingState }>();

  constructor(entity: Entity) {
    this.entity = entity;
  }

  setState(newState: BuildingState): void {
    if (this.currentState === newState) return;

    this.exitState(this.currentState);
    const previousState = this.currentState;
    this.currentState = newState;
    this.enterState(newState);

    this.onStateChanged.emit({ from: previousState, to: newState });
  }

  private enterState(state: BuildingState): void {
    const production = this.entity.getComponent(ProductionComponent);

    switch (state) {
      case BuildingState.Producing:
        production?.startProduction();
        break;
      case BuildingState.PoweredOff:
        production?.stopProduction();
        break;
      case BuildingState.Destroyed:
        // Trigger destruction visuals
        break;
    }
  }

  private exitState(state: BuildingState): void {
    // Cleanup if needed
  }

  getState(): BuildingState {
    return this.currentState;
  }
}
```

### Hierarchical State Machines

For complex behaviors, nest FSMs. Example: Unit AI

```
UnitAI (top-level FSM)
├── Idle
│   └── (internal) looking for targets
├── Combat (nested FSM)
│   ├── Approaching target
│   ├── Attacking
│   └── Retreating if health low
└── Dead
```

```typescript
class UnitAIStateMachine {
  private topLevelState: "idle" | "combat" | "dead" = "idle";
  private combatState?: "approaching" | "attacking" | "retreating";

  update(deltaTime: number): void {
    switch (this.topLevelState) {
      case "idle":
        this.updateIdleState();
        break;
      case "combat":
        this.updateCombatState();
        break;
    }
  }

  private updateCombatState(): void {
    switch (this.combatState) {
      case "approaching":
        // Move toward enemy
        break;
      case "attacking":
        // Fire weapons
        break;
      case "retreating":
        // Back away if low health
        break;
    }
  }
}
```

## Data-Driven Design: The Token Equivalent

In design systems, tokens separate *value* from *implementation*: `--color-primary-500` is the value; where it's used is the implementation.

Games do the same with **JSON config files**.

### JSON Balance Data

Store production rates, costs, tech trees in JSON:

```json
{
  "buildings": {
    "factory_basic": {
      "name": "Basic Factory",
      "cost": 500,
      "productionRate": 10.0,
      "powerConsumption": 20,
      "buildTime": 30,
      "maxHealth": 100
    },
    "factory_advanced": {
      "name": "Advanced Factory",
      "cost": 1500,
      "productionRate": 25.0,
      "powerConsumption": 50,
      "buildTime": 60,
      "maxHealth": 150
    },
    "refinery": {
      "name": "Refinery",
      "cost": 2000,
      "productionRate": 5.0,
      "powerConsumption": 100,
      "buildTime": 90,
      "maxHealth": 120
    }
  }
}
```

Load at runtime:

```typescript
class ConfigManager {
  private static instance: ConfigManager;
  private buildingConfig: any = {};

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  async loadBuildingConfig(): Promise<void> {
    const response = await fetch("/config/buildings.json");
    this.buildingConfig = await response.json();
  }

  getBuildingData(buildingType: string): any {
    return this.buildingConfig.buildings[buildingType];
  }
}

// Usage
const config = ConfigManager.getInstance();
const factoryData = config.getBuildingData("factory_basic");
const rate = factoryData.productionRate; // 10.0
```

**Why?** Designers change buildings.json without touching code. Test balance changes instantly.

## Event System Design: Decoupled Communication

Don't do this:
```typescript
// BAD: Direct coupling
productionComponent.produceItem();
storageComponent.addItem(item);
uiManager.updateDisplay();
```

Do this:
```typescript
// GOOD: Event-driven
productionComponent.onItemProduced.on(({ item, amount }) => {
  storageComponent.addResource(item, amount);
  uiManager.updateInventoryDisplay();
  analyticsManager.logProduction(item, amount);
});
```

**Why?** If you need a new listener (analytics), you just subscribe. No code changes to Production. This is the essence of decoupling.

```typescript
class EventEmitter<T> {
  private listeners: ((data: T) => void)[] = [];

  on(callback: (data: T) => void): void {
    this.listeners.push(callback);
  }

  off(callback: (data: T) => void): void {
    const index = this.listeners.indexOf(callback);
    if (index !== -1) this.listeners.splice(index, 1);
  }

  emit(data: T): void {
    for (const listener of this.listeners) {
      listener(data);
    }
  }
}
```

## Save/Load Architecture

Legion saves: colonized systems, built factories, unit positions, research unlocks.

### What to Save

```typescript
interface PlayerState {
  resources: {
    iron: number;
    copper: number;
    energy: number;
  };
  researchProgress: Map<string, number>;
  discoveredSystems: string[];
  playtimeSeconds: number;
}

interface BuildingInstance {
  id: string;
  type: string; // "factory_basic", "refinery", etc.
  position: { x: number; y: number; z: number };
  health: number;
  inventory: Map<string, number>;
}

interface SaveData {
  version: number;
  timestamp: number;
  playerState: PlayerState;
  buildings: BuildingInstance[];
  units: UnitInstance[];
  exploredSystems: string[];
}
```

### Serialization with IndexedDB

```typescript
class SaveManager {
  private dbName = "legion-saves";
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onupgradeneeded = (event: IDBVersionChangeEvent) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains("saves")) {
          db.createObjectStore("saves", { keyPath: "id" });
        }
      };

      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onerror = () => reject(request.error);
    });
  }

  async saveGame(slotName: string, saveData: SaveData): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["saves"], "readwrite");
      const store = transaction.objectStore("saves");

      const serialized = {
        id: slotName,
        version: saveData.version,
        timestamp: saveData.timestamp,
        data: JSON.stringify(saveData)
      };

      const request = store.put(serialized);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async loadGame(slotName: string): Promise<SaveData | null> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(["saves"], "readonly");
      const store = transaction.objectStore("saves");
      const request = store.get(slotName);

      request.onsuccess = () => {
        const result = request.result;
        if (result) {
          resolve(JSON.parse(result.data) as SaveData);
        } else {
          resolve(null);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }
}
```

### Versioning for Updates

As Legion evolves, old save formats break. Use **version tags**:

```typescript
function migrateSaveData(saveData: SaveData): SaveData {
  if (saveData.version < 2) {
    // v1 -> v2: Added "morale" field to buildings
    for (const building of saveData.buildings) {
      if (!(building as any).morale) {
        (building as any).morale = 50;
      }
    }
    saveData.version = 2;
  }

  if (saveData.version < 3) {
    // v2 -> v3: Restructured inventory from array to map
    // ... migration logic ...
    saveData.version = 3;
  }

  return saveData;
}
```

## Performance Architecture

Browsers must run at 60 FPS. Early decisions prevent rewrites.

### Object Pooling

Don't create/destroy bullets 1000 times per second. Create a pool, reuse them:

```typescript
class BulletPool {
  private available: Bullet[] = [];
  private active: Bullet[] = [];
  private pool: THREE.Object3D;

  constructor(size: number, scene: THREE.Scene) {
    this.pool = new THREE.Object3D();
    scene.add(this.pool);

    for (let i = 0; i < size; i++) {
      const bullet = new Bullet();
      this.pool.add(bullet.mesh);
      this.available.push(bullet);
    }
  }

  spawn(position: THREE.Vector3, direction: THREE.Vector3): Bullet {
    let bullet: Bullet;

    if (this.available.length > 0) {
      bullet = this.available.pop()!;
    } else {
      bullet = new Bullet();
      this.pool.add(bullet.mesh);
    }

    bullet.initialize(position, direction);
    this.active.push(bullet);
    return bullet;
  }

  returnBullet(bullet: Bullet): void {
    const index = this.active.indexOf(bullet);
    if (index !== -1) this.active.splice(index, 1);

    bullet.reset();
    this.available.push(bullet);
  }

  update(deltaTime: number): void {
    for (let i = this.active.length - 1; i >= 0; i--) {
      const bullet = this.active[i];
      bullet.update(deltaTime);

      if (bullet.isExpired()) {
        this.returnBullet(bullet);
      }
    }
  }
}
```

### Spatial Hashing for Collision

Instead of O(n²) collision checks, use spatial hashing:

```typescript
class SpatialHash {
  private cells: Map<string, Entity[]> = new Map();
  private cellSize: number = 100;

  addEntity(entity: Entity): void {
    const cellKey = this.getCellKey(entity.position);
    if (!this.cells.has(cellKey)) {
      this.cells.set(cellKey, []);
    }
    this.cells.get(cellKey)!.push(entity);
  }

  getNearby(position: THREE.Vector3, range: number): Entity[] {
    const nearby: Entity[] = [];
    const cellX = Math.floor(position.x / this.cellSize);
    const cellY = Math.floor(position.y / this.cellSize);

    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const key = `${cellX + dx},${cellY + dy}`;
        const entities = this.cells.get(key);
        if (entities) nearby.push(...entities);
      }
    }

    return nearby;
  }

  private getCellKey(pos: THREE.Vector3): string {
    const cellX = Math.floor(pos.x / this.cellSize);
    const cellY = Math.floor(pos.y / this.cellSize);
    return `${cellX},${cellY}`;
  }
}
```

### InstancedMesh for Many Objects

For 1000+ buildings with the same mesh, use InstancedMesh:

```typescript
const geometry = new THREE.BoxGeometry(10, 10, 10);
const material = new THREE.MeshStandardMaterial({ color: 0x888888 });
const instancedMesh = new THREE.InstancedMesh(geometry, material, 10000);

const matrix = new THREE.Matrix4();

for (let i = 0; i < buildingCount; i++) {
  matrix.setPosition(
    Math.random() * 10000,
    0,
    Math.random() * 10000
  );
  instancedMesh.setMatrixAt(i, matrix);
}

instancedMesh.instanceMatrix.needsUpdate = true;
scene.add(instancedMesh);
```

---

**Architecture is about enabling others—designers, artists, players, modders. Every design choice should increase expressiveness and decrease brittleness.**
