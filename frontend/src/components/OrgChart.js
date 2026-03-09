import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Users, Crown, Shield } from 'lucide-react';

// Custom Node Component
function CustomNode({ data }) {
  const isActive = data.status === 'active';
  const roleColor = data.role === 'admin' ? 'from-violet-500 to-purple-600' 
    : data.role === 'leader' ? 'from-blue-500 to-cyan-600' 
    : 'from-cyan-500 to-teal-600';

  const RoleIcon = data.role === 'admin' ? Crown : data.role === 'leader' ? Shield : Users;

  return (
    <div
      onClick={() => data.onNodeClick && data.onNodeClick(data)}
      className={`
        min-w-[220px] max-w-[280px] p-3 rounded-xl border-2 cursor-pointer
        transition-all duration-300 shadow-lg hover:shadow-2xl hover:scale-105
        ${isActive 
          ? 'bg-white dark:bg-slate-900 border-cyan-500/50 hover:border-cyan-500' 
          : 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 opacity-60'
        }
      `}
      data-testid={`org-node-${data.id}`}
    >
      {/* React Flow Handles for connections */}
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
      
      {/* Header with Role Icon */}
      <div className="flex items-center gap-2 mb-2">
        <div className={`p-1.5 rounded-lg bg-gradient-to-br ${roleColor}`}>
          <RoleIcon className="h-3.5 w-3.5 text-white" />
        </div>
        <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
          isActive 
            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
            : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-400'
        }`}>
          {isActive ? 'Active' : 'Inactive'}
        </span>
      </div>

      {/* Name */}
      <div className="font-bold text-sm text-slate-900 dark:text-white mb-1 truncate">
        {data.name}
      </div>

      {/* Info */}
      <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
        <span className="capitalize font-medium">{data.role}</span>
        <span className="font-bold text-cyan-600 dark:text-cyan-400">{data.comp_percentage}%</span>
      </div>

      {/* Team Size */}
      {data.team_size > 0 && (
        <div className="mt-2 pt-2 border-t border-slate-200 dark:border-slate-700">
          <div className="text-[10px] text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <Users className="h-3 w-3" />
            <span>{data.team_size} team member{data.team_size !== 1 ? 's' : ''}</span>
          </div>
        </div>
      )}
    </div>
  );
}

const nodeTypes = {
  custom: CustomNode,
};

export default function OrgChart({ data, onNodeClick }) {
  // Build nodes and edges from hierarchy data
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const nodes = [];
    const edges = [];
    const levelCounts = {};

    // Recursively build nodes and edges
    const buildNodes = (node, level = 0, parentId = null) => {
      if (!levelCounts[level]) levelCounts[level] = 0;
      const xPosition = levelCounts[level] * 320;
      const yPosition = level * 180;
      levelCounts[level]++;

      nodes.push({
        id: node.id,
        type: 'custom',
        position: { x: xPosition, y: yPosition },
        data: {
          ...node,
          team_size: node.children?.length || 0,
          onNodeClick,
        },
      });

      if (parentId) {
        edges.push({
          id: `${parentId}-${node.id}`,
          source: parentId,
          target: node.id,
          type: 'smoothstep',
          animated: node.status === 'active',
          style: { 
            stroke: node.status === 'active' ? '#22d3ee' : '#94a3b8',
            strokeWidth: 3,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: node.status === 'active' ? '#22d3ee' : '#94a3b8',
            width: 25,
            height: 25,
          },
          label: '',
          labelBgStyle: { fill: 'transparent' },
        });
      }

      if (node.children && node.children.length > 0) {
        node.children.forEach((child) => buildNodes(child, level + 1, node.id));
      }
    };

    if (data?.trees) {
      data.trees.forEach((tree) => buildNodes(tree));
    }

    return { nodes, edges };
  }, [data, onNodeClick]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onNodeDragStop = useCallback((event, node) => {
    // Custom logic when node drag stops (optional)
  }, []);

  if (!data?.trees || data.trees.length === 0) {
    return (
      <div className="h-[600px] flex items-center justify-center bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-800">
        <div className="text-center">
          <Users className="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
          <p className="text-slate-500 dark:text-slate-400 text-sm">No organization data to display</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[600px] border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden bg-white dark:bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeDragStop={onNodeDragStop}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.2}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        className="bg-white dark:bg-slate-950"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#cbd5e1" gap={20} size={1} className="bg-slate-100 dark:bg-slate-900" />
        <Controls className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg" />
      </ReactFlow>
    </div>
  );
}
