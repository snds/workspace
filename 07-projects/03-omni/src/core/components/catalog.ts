// ─── Component Catalog ───────────────────────────────────────────────────────
// Registry of all available component blueprints. Provides lookup, filtering,
// and search capabilities for the assets panel and code generation pipeline.

import type { ComponentBlueprint, ComponentCategory } from "./types";

export class ComponentCatalog {
  private blueprints: Map<string, ComponentBlueprint> = new Map();

  /** Register a component blueprint in the catalog */
  register(blueprint: ComponentBlueprint): void {
    this.blueprints.set(blueprint.id, blueprint);
  }

  /** Get a blueprint by its unique id */
  get(id: string): ComponentBlueprint | undefined {
    return this.blueprints.get(id);
  }

  /** Get all registered blueprints */
  getAll(): ComponentBlueprint[] {
    return Array.from(this.blueprints.values());
  }

  /** Get all blueprints in a specific category */
  getByCategory(category: ComponentCategory): ComponentBlueprint[] {
    return this.getAll().filter((bp) => bp.category === category);
  }

  /** Search blueprints by query string (matches name, tags, and description) */
  search(query: string): ComponentBlueprint[] {
    const q = query.toLowerCase().trim();
    if (!q) return this.getAll();

    return this.getAll().filter((bp) => {
      if (bp.name.toLowerCase().includes(q)) return true;
      if (bp.description?.toLowerCase().includes(q)) return true;
      if (bp.tags?.some((tag) => tag.toLowerCase().includes(q))) return true;
      return false;
    });
  }

  /** Get all categories that have at least one registered blueprint */
  getCategories(): ComponentCategory[] {
    const cats = new Set<ComponentCategory>();
    for (const bp of this.blueprints.values()) {
      cats.add(bp.category);
    }
    return Array.from(cats);
  }

  /** Check if a blueprint exists */
  has(id: string): boolean {
    return this.blueprints.has(id);
  }

  /** Remove a blueprint from the catalog */
  unregister(id: string): void {
    this.blueprints.delete(id);
  }
}
