# Game Data Systems: Save, Config, Procedural Generation, Analytics (Web)

The data layer that makes Legion flexible, tunable, and scalable. From IndexedDB saves to procedural generation to balance tuning.

## Save System with IndexedDB

Legion saves must capture: player progress, world state, discovered content, research unlocks, playtime.

### Data Structure

```typescript
interface SaveData {
  version: number;
  timestamp: number;
  playtimeSeconds: number;

  playerState: {
    resources: {
      iron: number;
      copper: number;
      aluminum: number;
      energy: number;
    };
    researchProgress: Map<string, number>;
    unlockedTechs: string[];
    factions: Map<string, "friendly" | "hostile" | "neutral">;
    knownSystems: string[];
  };

  worldState: {
    exploredSystems: Array<{
      systemId: string;
      discoveryTime: number;
      exploredCells: Set<string>;
    }>;
    buildings: Array<{
      id: string;
      type: string;
      position: { x: number; y: number; z: number };
      health: number;
      inventory: Map<string, number>;
      ownerId: string;
    }>;
    units: Array<{
      id: string;
      type: string;
      position: { x: number; y: number; z: number };
      health: number;
      ownerId: string;
      orders: any[];
    }>;
  };
}
```

### IndexedDB Manager

```typescript
class SaveManager {
  private dbName = "legion-saves";
  private storeName = "games";
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          const store = db.createObjectStore(this.storeName, { keyPath: "id" });
          store.createIndex("timestamp", "timestamp", { unique: false });
        }
      };

      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onerror = () => {
        console.error("Failed to open IndexedDB:", request.error);
        reject(request.error);
      };
    });
  }

  async saveGame(slotName: string, saveData: SaveData): Promise<void> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readwrite");
      const store = transaction.objectStore(this.storeName);

      const serialized = {
        id: slotName,
        version: saveData.version,
        timestamp: Date.now(),
        data: JSON.stringify(saveData) // Serialize to JSON
      };

      const request = store.put(serialized);

      request.onsuccess = () => {
        console.log(`Game saved to slot: ${slotName}`);
        resolve();
      };

      request.onerror = () => {
        console.error("Failed to save game:", request.error);
        reject(request.error);
      };
    });
  }

  async loadGame(slotName: string): Promise<SaveData | null> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readonly");
      const store = transaction.objectStore(this.storeName);
      const request = store.get(slotName);

      request.onsuccess = () => {
        const result = request.result;
        if (result) {
          const saveData = JSON.parse(result.data) as SaveData;
          // Migration happens here
          const migrated = this.migrateIfNeeded(saveData);
          resolve(migrated);
        } else {
          resolve(null);
        }
      };

      request.onerror = () => {
        console.error("Failed to load game:", request.error);
        reject(request.error);
      };
    });
  }

  async listSaves(): Promise<Array<{ id: string; timestamp: number }>> {
    if (!this.db) throw new Error("Database not initialized");

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], "readonly");
      const store = transaction.objectStore(this.storeName);
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(
          request.result.map((save) => ({
            id: save.id,
            timestamp: save.timestamp
          }))
        );
      };

      request.onerror = () => reject(request.error);
    });
  }

  private migrateIfNeeded(saveData: SaveData): SaveData {
    if (saveData.version < 2) {
      // v1 -> v2: Add new fields with defaults
      if (!saveData.playerState.factions) {
        saveData.playerState.factions = new Map();
      }
      saveData.version = 2;
    }

    if (saveData.version < 3) {
      // v2 -> v3: Restructure data if needed
      saveData.version = 3;
    }

    return saveData;
  }
}
```

## Configuration & Balance Data

Store all **tunable values** in JSON so designers don't touch code.

### Building Balance Config

```json
{
  "buildings": {
    "factory_basic": {
      "name": "Basic Factory",
      "cost": 500,
      "buildTime": 30,
      "productionRate": 10.0,
      "powerConsumption": 20,
      "maxHealth": 100,
      "inputs": {
        "ore": 1.0
      },
      "output": "metal",
      "outputAmount": 1.0
    },
    "factory_advanced": {
      "name": "Advanced Factory",
      "cost": 1500,
      "buildTime": 60,
      "productionRate": 25.0,
      "powerConsumption": 50,
      "maxHealth": 150,
      "inputs": {
        "ore": 2.0
      },
      "output": "metal",
      "outputAmount": 2.5
    },
    "refinery": {
      "name": "Refinery",
      "cost": 2000,
      "buildTime": 90,
      "productionRate": 5.0,
      "powerConsumption": 100,
      "maxHealth": 120,
      "inputs": {
        "crude_ore": 1.0
      },
      "output": "pure_ore",
      "outputAmount": 1.0
    }
  }
}
```

### Configuration Loader

```typescript
class ConfigManager {
  private static instance: ConfigManager;
  private configs: Map<string, any> = new Map();

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  async loadConfig(name: string, path: string): Promise<void> {
    try {
      const response = await fetch(path);
      const data = await response.json();
      this.configs.set(name, data);
      console.log(`Loaded config: ${name}`);
    } catch (error) {
      console.error(`Failed to load config ${name}:`, error);
    }
  }

  getConfig<T>(name: string): T {
    const config = this.configs.get(name);
    if (!config) throw new Error(`Config not found: ${name}`);
    return config as T;
  }

  getBuildingData(buildingType: string): any {
    const buildings = this.configs.get("buildings") ?? {};
    return buildings[buildingType];
  }

  // Hot reload for dev
  async reloadConfig(name: string, path: string): Promise<void> {
    await this.loadConfig(name, `${path}?t=${Date.now()}`);
    console.log(`Reloaded config: ${name}`);
  }
}

// Usage
const config = ConfigManager.getInstance();
await config.loadConfig("buildings", "/config/buildings.json");
await config.loadConfig("difficulty", "/config/difficulty.json");

const factoryData = config.getBuildingData("factory_basic");
console.log(`Factory cost: ${factoryData.cost}`);
```

## Procedural Generation

Legion's galaxy is mostly **procedurally generated**: star systems, asteroid fields, resource deposits.

### Star System Generation (Seeded)

```typescript
class StarSystemGenerator {
  private seed: number;

  constructor(seed: number) {
    this.seed = seed;
  }

  generate(coords: { x: number; y: number }): StarSystem {
    const rng = this.createSeededRandom(coords.x, coords.y);

    const system: StarSystem = {
      coordinates: coords,
      name: this.generateSystemName(rng),
      starMass: rng.next() * 2.5 + 0.5, // 0.5 to 3.0 solar masses
      planets: this.generatePlanets(rng),
      asteroidFields: this.generateAsteroidFields(rng)
    };

    return system;
  }

  private generatePlanets(rng: SeededRandom): Planet[] {
    const planets: Planet[] = [];
    const count = Math.floor(rng.next() * 8) + 2; // 2-10 planets

    for (let i = 0; i < count; i++) {
      planets.push({
        id: `planet_${i}`,
        orbitDistance: rng.next() * 50000 + 500,
        radius: rng.next() * 12000 + 3000,
        type: this.determinePlanetType(rng),
        resources: this.generateResourceComposition(rng)
      });
    }

    return planets;
  }

  private generateAsteroidFields(rng: SeededRandom): AsteroidField[] {
    const fields: AsteroidField[] = [];
    const count = Math.floor(rng.next() * 4) + 1; // 1-5 fields

    for (let i = 0; i < count; i++) {
      fields.push({
        id: `field_${i}`,
        position: {
          x: (rng.next() - 0.5) * 100000,
          y: (rng.next() - 0.5) * 50000,
          z: (rng.next() - 0.5) * 100000
        },
        asteroidCount: Math.floor(rng.next() * 500) + 100,
        resources: this.generateResourceComposition(rng)
      });
    }

    return fields;
  }

  private generateResourceComposition(rng: SeededRandom): {
    [resource: string]: number;
  } {
    const composition: { [key: string]: number } = {};
    const resourceTypes = ["iron", "copper", "aluminum", "rare_earth"];

    for (const resource of resourceTypes) {
      composition[resource] = rng.next() * 100;
    }

    return composition;
  }

  private determinePlanetType(rng: SeededRandom): string {
    const roll = rng.next();
    if (roll < 0.3) return "rocky";
    if (roll < 0.6) return "ice";
    if (roll < 0.8) return "gas_giant";
    return "terrestrial";
  }

  private generateSystemName(rng: SeededRandom): string {
    const prefixes = ["Alpha", "Beta", "Gamma", "Delta"];
    const suffixes = ["Centauri", "Draconis", "Virginis", "Serpentis"];

    const prefix = prefixes[Math.floor(rng.next() * prefixes.length)];
    const suffix = suffixes[Math.floor(rng.next() * suffixes.length)];
    const number = Math.floor(rng.next() * 1000);

    return `${prefix} ${suffix} ${number}`;
  }

  private createSeededRandom(x: number, y: number): SeededRandom {
    // Xorshift PRNG seeded by coordinates
    let seed = x * 73856093 ^ y * 19349663;
    return new SeededRandom(seed);
  }
}

class SeededRandom {
  private seed: number;

  constructor(seed: number) {
    this.seed = seed;
  }

  next(): number {
    this.seed ^= this.seed << 13;
    this.seed ^= this.seed >> 17;
    this.seed ^= this.seed << 5;
    return ((this.seed >>> 0) / 0xffffffff);
  }
}

interface StarSystem {
  coordinates: { x: number; y: number };
  name: string;
  starMass: number;
  planets: Planet[];
  asteroidFields: AsteroidField[];
}

interface Planet {
  id: string;
  orbitDistance: number;
  radius: number;
  type: string;
  resources: { [resource: string]: number };
}

interface AsteroidField {
  id: string;
  position: { x: number; y: number; z: number };
  asteroidCount: number;
  resources: { [resource: string]: number };
}
```

### Perlin Noise for Terrain

```typescript
// Use a library like Perlin.js or Simplex.js for noise
import SimplexNoise from "simplex-noise";

class TerrainGenerator {
  private noise: SimplexNoise;
  private scale: number = 0.01;
  private amplitude: number = 5000;

  constructor(seed: string) {
    this.noise = new SimplexNoise(() => {
      // Seeded random using seed string
      let hash = 0;
      for (let i = 0; i < seed.length; i++) {
        hash = ((hash << 5) - hash) + seed.charCodeAt(i);
        hash = hash & hash;
      }
      return (hash & 0x7fffffff) / 0x7fffffff;
    });
  }

  generateHeightMap(width: number, height: number): number[] {
    const heightMap: number[] = [];

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let noiseValue = this.noise.noise2D(x * this.scale, y * this.scale);

        // Fractal Brownian Motion (multiple octaves)
        let amplitude = 1;
        let frequency = 1;
        for (let i = 1; i < 4; i++) {
          frequency *= 2;
          amplitude *= 0.5;
          noiseValue += this.noise.noise2D(
            x * this.scale * frequency,
            y * this.scale * frequency
          ) * amplitude;
        }

        const height = (noiseValue + 1) * this.amplitude;
        heightMap.push(height);
      }
    }

    return heightMap;
  }
}
```

## Analytics & Telemetry

Track player behavior for balance tuning and engagement:

```typescript
class AnalyticsManager {
  private queue: AnalyticsEvent[] = [];
  private batchSize: number = 10;
  private flushInterval: number = 30000; // 30 seconds
  private serverUrl: string = "/api/analytics";

  constructor() {
    // Auto-flush periodically
    setInterval(() => this.flush(), this.flushInterval);
  }

  logResourceHarvested(resourceType: string, amount: number): void {
    this.queue.push({
      event: "resource_harvested",
      timestamp: Date.now(),
      data: { resource_type: resourceType, amount }
    });

    if (this.queue.length >= this.batchSize) {
      this.flush();
    }
  }

  logBuildingConstructed(buildingType: string, position: { x: number; y: number }): void {
    this.queue.push({
      event: "building_constructed",
      timestamp: Date.now(),
      data: { building_type: buildingType, grid_x: position.x / 200, grid_y: position.y / 200 }
    });
  }

  logCombatEngagement(
    allyCount: number,
    enemyCount: number,
    playerWon: boolean
  ): void {
    this.queue.push({
      event: "combat_engagement",
      timestamp: Date.now(),
      data: { ally_units: allyCount, enemy_units: enemyCount, player_won: playerWon }
    });
  }

  logPlaytimeMilestone(playtimeSeconds: number): void {
    this.queue.push({
      event: "playtime_milestone",
      timestamp: Date.now(),
      data: { playtime_seconds: playtimeSeconds }
    });
  }

  async flush(): Promise<void> {
    if (this.queue.length === 0) return;

    const events = this.queue.splice(0, this.batchSize);

    try {
      await fetch(this.serverUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events })
      });
      console.log(`Flushed ${events.length} analytics events`);
    } catch (error) {
      console.error("Failed to send analytics:", error);
      // Re-queue events on failure
      this.queue.push(...events);
    }
  }
}

interface AnalyticsEvent {
  event: string;
  timestamp: number;
  data: { [key: string]: any };
}
```

## Mod Support Architecture

Design systems so the community can extend Legion.

### JSON-Based Mod Config

```json
{
  "modId": "community-factories",
  "name": "Community Factories",
  "version": "1.0.0",
  "author": "modder",
  "description": "Adds new factory types",
  "buildings": [
    {
      "id": "mega_factory",
      "name": "Mega Factory",
      "baseType": "factory_advanced",
      "overrides": {
        "productionRate": 50.0,
        "powerConsumption": 100,
        "cost": 5000
      }
    }
  ]
}
```

### Mod Loader

```typescript
class ModManager {
  private mods: Map<string, ModConfig> = new Map();
  private configManager = ConfigManager.getInstance();

  async loadMod(modId: string, modPath: string): Promise<void> {
    try {
      const response = await fetch(`${modPath}/mod.json`);
      const modConfig = await response.json() as ModConfig;

      // Load mod buildings
      if (modConfig.buildings) {
        const buildingsConfig = this.configManager.getConfig("buildings");
        for (const building of modConfig.buildings) {
          // Apply overrides to existing buildings or add new ones
          const baseBuilding = buildingsConfig[building.baseType] || {};
          buildingsConfig[building.id] = {
            ...baseBuilding,
            ...building.overrides
          };
        }
      }

      this.mods.set(modId, modConfig);
      console.log(`Loaded mod: ${modConfig.name}`);
    } catch (error) {
      console.error(`Failed to load mod ${modId}:`, error);
    }
  }

  async loadAllMods(modsPath: string): Promise<void> {
    try {
      const response = await fetch(`${modsPath}/manifest.json`);
      const manifest = await response.json();

      for (const modId of manifest.enabled_mods) {
        await this.loadMod(modId, `${modsPath}/${modId}`);
      }
    } catch (error) {
      console.error("Failed to load mod manifest:", error);
    }
  }

  isModLoaded(modId: string): boolean {
    return this.mods.has(modId);
  }
}

interface ModConfig {
  modId: string;
  name: string;
  version: string;
  author: string;
  description: string;
  buildings?: Array<{
    id: string;
    name: string;
    baseType: string;
    overrides: { [key: string]: any };
  }>;
}
```

---

**Data is king. Separate values from code, expose balance through JSON configs, track behavior to guide design. This is how Legion scales from prototype to a living, evolving game.**
