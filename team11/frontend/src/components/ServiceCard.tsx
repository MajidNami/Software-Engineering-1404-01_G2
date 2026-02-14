import React from 'react';

interface TeamLink {
  label: string;
  url: string;
}

interface ServiceCardProps {
  icon: string;
  title: string;
  description: string;
  teams: TeamLink[];
}

const ServiceCard: React.FC<ServiceCardProps> = ({ icon, title, description, teams }) => {
  return (
    <div className="group relative flex flex-col p-5 bg-white rounded-[20px] shadow-sm border border-white/60 transition-all duration-300 hover:-translate-y-2 hover:shadow-xl overflow-hidden">
      {/* Side Accent Line */}
      <div className="absolute right-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-persian-gold to-leaf-green opacity-60 group-hover:opacity-100 transition-opacity" />
      
      <div className="flex items-center gap-4 mb-6">
        {/* Icon Container */}
        <div className="flex items-center justify-center w-14 h-14 bg-bg-light rounded-xl text-forest-green text-xl group-hover:bg-forest-green group-hover:text-white transition-colors shadow-inner">
          <i className={icon}></i>
        </div>
        
        <div className="flex flex-col flex-1">
          <h3 className="bg-forest-green text-white px-3 py-1 rounded-lg text-sm font-bold w-fit mb-1 shadow-sm">
            {title}
          </h3>
          <p className="text-gray-500 text-xs font-medium leading-tight">
            {description}
          </p>
        </div>
      </div>

      {/* Buttons Area */}
      <div className="flex flex-wrap gap-2 mt-auto">
        {teams.map((team, idx) => (
          <a 
            key={idx}
            href={team.url}
            className="flex-1 min-w-[80px] text-center py-2 text-xs font-bold text-forest-green bg-forest-green/5 border border-forest-green/10 rounded-lg hover:bg-forest-green hover:text-white transition-all"
          >
            {team.label}
          </a>
        ))}
      </div>
    </div>
  );
};

export default ServiceCard;