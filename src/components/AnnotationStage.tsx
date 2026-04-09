import { useState } from 'react';
import { DndContext, useDraggable, useDroppable, DragEndEvent, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import clsx from 'clsx';

interface AnnotationItem {
  name: string;
}

interface AnnotationStageProps {
  imagePath: string;
  annotations: AnnotationItem[];
  onComplete: (isComplete: boolean) => void;
}

function DraggableChip({ id, name, isPlaced }: { id: string; name: string; isPlaced: boolean }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: id,
  });

  const style = {
    transform: CSS.Translate.toString(transform),
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={clsx(
        "px-4 py-2 rounded-xl text-sm font-bold shadow-lg touch-none transition-colors",
        isPlaced ? "bg-brand-success text-white" : "bg-brand-accent text-white",
        isDragging ? "opacity-80 z-50 scale-105" : "z-10"
      )}
    >
      {name}
    </div>
  );
}

export default function AnnotationStage({ imagePath, annotations, onComplete }: AnnotationStageProps) {
  const [placedItems, setPlacedItems] = useState<string[]>([]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5, // 5px tolerance for touch
      },
    })
  );

  const { setNodeRef, isOver } = useDroppable({
    id: 'image-area',
  });

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    
    if (over && over.id === 'image-area') {
      if (!placedItems.includes(active.id as string)) {
        const newPlaced = [...placedItems, active.id as string];
        setPlacedItems(newPlaced);
        if (newPlaced.length === annotations.length) {
          onComplete(true);
        }
      }
    }
  };

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
      <div className="flex flex-col gap-4">
        <p className="text-sm text-brand-muted">
          拖拽标签到图像区域内完成标注。
        </p>
        
        {/* Tray */}
        <div className="flex flex-wrap gap-3 min-h-[60px] p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
          {annotations.map((ann, idx) => {
            const id = `ann-${idx}`;
            if (placedItems.includes(id)) return null;
            return <DraggableChip key={id} id={id} name={ann.name} isPlaced={false} />;
          })}
          {placedItems.length === annotations.length && (
            <span className="text-brand-success font-medium text-sm my-auto">所有标签已放置！</span>
          )}
        </div>

        {/* Image Area */}
        <div 
          ref={setNodeRef}
          className={clsx(
            "relative w-full aspect-video rounded-xl overflow-hidden border-2 transition-colors",
            isOver ? "border-brand-accent bg-brand-accent/10" : "border-slate-700 bg-slate-900"
          )}
        >
          {imagePath && (
            <img src={imagePath} alt="标注目标" className="w-full h-full object-contain" />
          )}
          <div className="absolute inset-0 pointer-events-none p-4 flex flex-wrap gap-2 content-end">
            {annotations.map((ann, idx) => {
              const id = `ann-${idx}`;
              if (!placedItems.includes(id)) return null;
              return <DraggableChip key={`placed-${id}`} id={`placed-${id}`} name={ann.name} isPlaced={true} />;
            })}
          </div>
        </div>
      </div>
    </DndContext>
  );
}
