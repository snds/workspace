import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

export type ActiveLeftPanel = "design" | "assets" | "tokens" | "code";
export type ToolMode =
  | "select"
  | "hand"
  | "frame"
  | "shape"
  | "text"
  | "pen"
  | "pen-path";

export type AppTheme = "dark" | "light";

interface UIState {
  leftPanelVisible: boolean;
  rightPanelVisible: boolean;
  leftPanelWidth: number;
  rightPanelWidth: number;
  activeLeftPanel: ActiveLeftPanel;
  activeTool: ToolMode;
  zoom: number;
  theme: AppTheme;
  inspectMode: boolean;
  pagesPanelHeight: number;
  /** Canvas background color as hex string, or null to use the theme default */
  canvasBgHex: string | null;
  /** Canvas background opacity 0–1 */
  canvasBgAlpha: number;
  /** Whether the keyboard shortcuts reference modal is open */
  showKeyboardShortcuts: boolean;
  /** When true, both side panels are hidden (presentation mode) */
  panelsHidden: boolean;
  /** Snap to nearby objects during move/resize */
  snapEnabled: boolean;
  /** Show rulers along canvas edges */
  showRulers: boolean;
  /** Show pixel grid at high zoom */
  showGrid: boolean;
}

interface UIActions {
  toggleLeftPanel(): void;
  toggleRightPanel(): void;
  setLeftPanelWidth(width: number): void;
  setRightPanelWidth(width: number): void;
  setActiveLeftPanel(panel: ActiveLeftPanel): void;
  setActiveTool(tool: ToolMode): void;
  setZoom(zoom: number): void;
  zoomIn(): void;
  zoomOut(): void;
  resetZoom(): void;
  toggleTheme(): void;
  toggleInspectMode(): void;
  setPagesPanelHeight(height: number): void;
  setCanvasBg(hex: string | null, alpha: number): void;
  toggleKeyboardShortcuts(): void;
  setShowKeyboardShortcuts(show: boolean): void;
  toggleAllPanels(): void;
  toggleSnap(): void;
  toggleRulers(): void;
  toggleGrid(): void;
}

const MIN_ZOOM = 0.1;
const MAX_ZOOM = 8;
const ZOOM_STEP = 0.1;

export const useUIStore = create<UIState & UIActions>()(
  immer((set) => ({
    leftPanelVisible: true,
    rightPanelVisible: true,
    leftPanelWidth: 300,
    rightPanelWidth: 300,
    activeLeftPanel: "design",
    activeTool: "select",
    zoom: 1,
    theme: "dark",
    inspectMode: false,
    pagesPanelHeight: 120,
    canvasBgHex: null,
    canvasBgAlpha: 1,
    showKeyboardShortcuts: false,
    panelsHidden: false,
    snapEnabled: true,
    showRulers: true,
    showGrid: false,

    toggleLeftPanel: () =>
      set((s) => {
        s.leftPanelVisible = !s.leftPanelVisible;
      }),
    toggleRightPanel: () =>
      set((s) => {
        s.rightPanelVisible = !s.rightPanelVisible;
      }),
    setLeftPanelWidth: (w) =>
      set((s) => {
        s.leftPanelWidth = Math.max(300, Math.min(480, w));
      }),
    setRightPanelWidth: (w) =>
      set((s) => {
        s.rightPanelWidth = Math.max(285, Math.min(480, w));
      }),
    setActiveLeftPanel: (p) =>
      set((s) => {
        s.activeLeftPanel = p;
      }),
    setActiveTool: (tool) =>
      set((s) => {
        s.activeTool = tool;
      }),
    setZoom: (z) =>
      set((s) => {
        s.zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, z));
      }),
    zoomIn: () =>
      set((s) => {
        s.zoom = Math.min(MAX_ZOOM, +(s.zoom + ZOOM_STEP).toFixed(2));
      }),
    zoomOut: () =>
      set((s) => {
        s.zoom = Math.max(MIN_ZOOM, +(s.zoom - ZOOM_STEP).toFixed(2));
      }),
    resetZoom: () =>
      set((s) => {
        s.zoom = 1;
      }),
    toggleTheme: () =>
      set((s) => {
        s.theme = s.theme === "dark" ? "light" : "dark";
      }),
    toggleInspectMode: () =>
      set((s) => {
        s.inspectMode = !s.inspectMode;
      }),
    setPagesPanelHeight: (h) =>
      set((s) => {
        s.pagesPanelHeight = Math.max(60, Math.min(400, h));
      }),
    setCanvasBg: (hex, alpha) =>
      set((s) => {
        s.canvasBgHex = hex;
        s.canvasBgAlpha = Math.max(0, Math.min(1, alpha));
      }),
    toggleKeyboardShortcuts: () =>
      set((s) => { s.showKeyboardShortcuts = !s.showKeyboardShortcuts; }),
    setShowKeyboardShortcuts: (show) =>
      set((s) => { s.showKeyboardShortcuts = show; }),
    toggleAllPanels: () =>
      set((s) => { s.panelsHidden = !s.panelsHidden; }),
    toggleSnap: () =>
      set((s) => { s.snapEnabled = !s.snapEnabled; }),
    toggleRulers: () =>
      set((s) => { s.showRulers = !s.showRulers; }),
    toggleGrid: () =>
      set((s) => { s.showGrid = !s.showGrid; }),
  }))
);
