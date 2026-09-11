import { useEffect, useRef } from "react";
import { Transformer } from "react-konva";
import type Konva from "konva";
import { useCanvasStore } from "@/stores/canvas.store";

interface SelectionTransformerProps {
  selectedIds: string[];
  zoom: number;
  layerRef: React.RefObject<Konva.Layer | null>;
}

export function SelectionTransformer({ selectedIds, zoom, layerRef }: SelectionTransformerProps) {
  const trRef = useRef<Konva.Transformer>(null);
  const { updateNodes } = useCanvasStore();

  useEffect(() => {
    const tr = trRef.current;
    const layer = layerRef.current;
    if (!tr || !layer) return;

    if (selectedIds.length === 0) {
      tr.nodes([]);
      layer.batchDraw();
      return;
    }

    const nodes = selectedIds
      .map((id) => layer.findOne(`#${id}`))
      .filter(Boolean) as Konva.Node[];

    tr.nodes(nodes);
    layer.batchDraw();
  }, [selectedIds, layerRef]);

  // Scale anchors with zoom so they stay visually consistent
  const anchorSize = Math.round(8 / zoom);

  function handleTransformEnd() {
    const tr = trRef.current;
    if (!tr) return;

    const patches = tr.nodes().map((node) => {
      const scaleX = node.scaleX();
      const scaleY = node.scaleY();
      // Bake scale into width/height and reset scale to 1
      const newWidth = Math.max(1, (node.width ? node.width() : 1) * scaleX);
      const newHeight = Math.max(1, (node.height ? node.height() : 1) * scaleY);
      node.scaleX(1);
      node.scaleY(1);
      return {
        id: node.id(),
        x: node.x(),
        y: node.y(),
        width: newWidth,
        height: newHeight,
        rotation: node.rotation(),
      };
    });

    updateNodes(patches);
  }

  if (selectedIds.length === 0) return null;

  return (
    <Transformer
      ref={trRef}
      anchorSize={anchorSize}
      anchorCornerRadius={2}
      anchorStroke="#6366f1"
      anchorFill="#ffffff"
      borderStroke="#6366f1"
      borderStrokeWidth={1 / zoom}
      rotateEnabled={true}
      keepRatio={false}
      onTransformEnd={handleTransformEnd}
    />
  );
}
