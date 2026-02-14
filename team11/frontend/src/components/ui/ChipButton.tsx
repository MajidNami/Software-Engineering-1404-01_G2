import React from 'react';

interface ChipButtProps {
  label: string;
  isSelected: boolean;
  onClick: () => void;
  onDelete?: () => void; // New optional prop
}

const ChipButt: React.FC<ChipButtProps> = ({ label, isSelected, onClick, onDelete }) => (
  <div className="relative group items-center flex">
    <button
      type="button"
      onClick={onClick}
      className={`
        px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center
        ${isSelected
          ? 'bg-[#2E7D32] text-white shadow-lg scale-105'
          : 'bg-[#37474F]/10 text-[#37474F] hover:bg-[#37474F]/20'
        }
        ${onDelete ? 'pl-8' : ''} 
      `}
    >
      {label}
      {isSelected && <i className="fa-solid fa-check mr-3 text-[10px]"></i>}
    </button>

    {onDelete && (
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="absolute left-2 top-1/2 -translate-y-1/2 text-red-5 transition-opacity hover:text-red-700 p-1"
      >
        <i className="fa-solid fa-xmark text-sm"></i>
      </button>
    )}
  </div>
);

export default ChipButt;