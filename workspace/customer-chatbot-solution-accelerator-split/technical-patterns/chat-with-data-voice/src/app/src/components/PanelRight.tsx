import { Children, isValidElement, useState, type MouseEvent, type ReactElement, type ReactNode } from 'react';
import { PanelRightToolbar } from '@/components/PanelRightToolbar';

interface PanelRightProps {
  panelWidth?: number;
  panelResize?: boolean;
  children?: ReactNode;
}

export function PanelRight({ panelWidth = 325, panelResize = true, children }: PanelRightProps) {
  const [width, setWidth] = useState(panelWidth);
  const [isHandleHovered, setIsHandleHovered] = useState(false);

  const handleMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    if (!panelResize) return;
    const startX = e.clientX;
    const startWidth = width;

    const onMouseMove = (moveEvent: globalThis.MouseEvent) => {
      const newWidth = Math.min(500, Math.max(256, startWidth - (moveEvent.clientX - startX)));
      setWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.body.style.userSelect = '';
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    document.body.style.userSelect = 'none';
  };

  const childrenArray = Children.toArray(children) as ReactElement[];
  const toolbar = childrenArray.find((child) => isValidElement(child) && child.type === PanelRightToolbar);
  const content = childrenArray.filter((child) => !(isValidElement(child) && child.type === PanelRightToolbar));

  return (
    <section
      className="relative flex h-full min-h-0 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
      style={{ width: panelResize ? `${width}px` : undefined }}
    >
      {toolbar}
      <div className="flex-1 overflow-y-auto">{content}</div>
      {panelResize ? (
        <div
          className="absolute left-0 top-0 h-full w-0.5 cursor-ew-resize"
          onMouseDown={handleMouseDown}
          onMouseEnter={() => setIsHandleHovered(true)}
          onMouseLeave={() => setIsHandleHovered(false)}
          style={{ backgroundColor: isHandleHovered ? 'var(--colorNeutralStroke2)' : 'transparent' }}
        />
      ) : null}
    </section>
  );
}
