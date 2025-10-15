import * as React from "react";
import { X } from "lucide-react";
import { cn } from '../../lib/utils';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PROFESSIONS_DATA } from "@/data/professions";
import { Badge } from "@/components/ui/badge";

interface ProfessionSelectProps {
  value: string[];
  onChange: (value: string[]) => void;
  maxSelections?: number;
  className?: string;
}

export function ProfessionSelect({
  value = [],
  onChange,
  maxSelections = 50,
  className,
}: ProfessionSelectProps) {
  const [selectedProfession, setSelectedProfession] =
    React.useState<string>("");

  const handleSelect = (profession: string) => {
    if (!value.includes(profession) && value.length < maxSelections) {
      onChange([...value, profession]);
    }
    setSelectedProfession("");
  };

  const removeProfession = (profession: string) => {
    onChange(value.filter((item) => item !== profession));
  };

  const availableProfessions = Object.entries(PROFESSIONS_DATA).filter(
    ([name]) => !value.includes(name),
  );

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex gap-2">
        <Select
          value={selectedProfession}
          onValueChange={(val) => {
            if (val) {
              handleSelect(val);
            }
          }}
          disabled={value.length >= maxSelections}
        >
          <SelectTrigger className="w-full">
            <SelectValue
              placeholder={
                value.length === 0
                  ? "Sélectionnez une profession..."
                  : `Ajouter une profession (${value.length}/${maxSelections})`
              }
            />
          </SelectTrigger>
          <SelectContent>
            {availableProfessions.map(([name, data]) => (
              <SelectItem key={name} value={name}>
                <div className="flex items-center gap-2">
                  <span className="text-lg">{data.icon}</span>
                  <div>
                    <div className="font-medium">{name}</div>
                    <div className="text-xs text-muted-foreground">
                      {data.roles?.join(", ")}
                    </div>
                  </div>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {value.length > 0 && (
        <div className="mt-4">
          <h4 className="mb-2 text-sm font-medium">
            Professions sélectionnées
          </h4>
          <div className="flex flex-wrap gap-2">
            {value.map((profession) => (
              <Badge
                key={profession}
                variant="outline"
                className="flex items-center gap-1"
              >
                {PROFESSIONS_DATA[profession]?.icon} {profession}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeProfession(profession);
                  }}
                  className="ml-1 rounded-full p-0.5 hover:bg-muted"
                  aria-label={`Retirer ${profession}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>
      )}
      {maxSelections && (
        <p className="text-xs text-muted-foreground">
          {value.length} / {maxSelections} sélectionnés
        </p>
      )}
    </div>
  );
}
