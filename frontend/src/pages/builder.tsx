import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function BuilderPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Squad Builder</h2>
          <p className="text-muted-foreground">
            Create and optimize your WvW squad composition
          </p>
        </div>
        <Button>Save Composition</Button>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Squad Configuration */}
        <div className="space-y-4 rounded-lg border p-6">
          <h3 className="text-lg font-medium">Squad Configuration</h3>
          
          <div className="space-y-2">
            <Label htmlFor="squad-name">Squad Name</Label>
            <Input id="squad-name" placeholder="My Awesome Squad" />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="squad-size">Squad Size</Label>
            <Select defaultValue="15">
              <SelectTrigger>
                <SelectValue placeholder="Select squad size" />
              </SelectTrigger>
              <SelectContent>
                {[5, 10, 15, 20, 25, 30, 40, 50].map((size) => (
                  <SelectItem key={size} value={size.toString()}>
                    {size} Players
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="playstyle">Playstyle</Label>
            <Select defaultValue="balanced">
              <SelectTrigger>
                <SelectValue placeholder="Select playstyle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="balanced">Balanced</SelectItem>
                <SelectItem value="offensive">Offensive</SelectItem>
                <SelectItem value="defensive">Defensive</SelectItem>
                <SelectItem value="zerg">Zerg</SelectItem>
                <SelectItem value="havoc">Havoc</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Role Distribution */}
        <div className="space-y-4 rounded-lg border p-6 md:col-span-2">
          <h3 className="text-lg font-medium">Role Distribution</h3>
          <div className="grid gap-4 md:grid-cols-2">
            {["Healer", "Support", "DPS", "CC", "Roamer"].map((role) => (
              <div key={role} className="space-y-2 rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{role}</span>
                  <span className="text-sm text-muted-foreground">0/0</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-secondary">
                  <div className="h-full w-0 bg-primary transition-all" style={{ width: '0%' }} />
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2">
                  <Button variant="outline" size="sm" className="text-xs">
                    Add {role}
                  </Button>
                  <Button variant="outline" size="sm" className="text-xs" disabled>
                    Auto-Fill
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Profession Selection */}
      <div className="rounded-lg border p-6">
        <h3 className="mb-4 text-lg font-medium">Available Professions</h3>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {[
            "Guardian", "Warrior", "Engineer", "Ranger", "Thief",
            "Elementalist", "Mesmer", "Necromancer", "Revenant"
          ].map((profession) => (
            <div key={profession} className="flex flex-col items-center space-y-2 rounded-lg border p-4 text-center">
              <div className="h-16 w-16 rounded-full bg-muted">
                {/* Profession icon would go here */}
              </div>
              <span className="text-sm font-medium">{profession}</span>
              <Button variant="outline" size="sm" className="w-full">
                Add to Squad
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
