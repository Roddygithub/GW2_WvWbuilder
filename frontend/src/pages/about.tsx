import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function AboutPage() {
  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">
          About GW2 WvW Builder
        </h2>
        <p className="text-muted-foreground">
          Optimizing your World vs World experience in Guild Wars 2
        </p>
      </div>

      <div className="prose max-w-none dark:prose-invert">
        <p>
          GW2 WvW Builder is a tool designed to help Guild Wars 2 players
          create, optimize, and share squad compositions for World vs World
          battles. Whether you're leading a small havoc squad or commanding a
          full zerg, our tool helps you build the perfect team composition.
        </p>

        <h3>Features</h3>
        <ul>
          <li>
            <strong>Intelligent Composition Builder</strong> - Create optimized
            squad compositions based on your group size and playstyle
          </li>
          <li>
            <strong>Role Distribution</strong> - Balance your squad with the
            right mix of support, damage, and utility roles
          </li>
          <li>
            <strong>Profession Synergies</strong> - Get suggestions for
            profession combinations that work well together
          </li>
          <li>
            <strong>Share & Collaborate</strong> - Share your compositions with
            your guild or the community
          </li>
          <li>
            <strong>GW2 API Integration</strong> - Pull character and build data
            directly from the Guild Wars 2 API
          </li>
        </ul>

        <h3>How It Works</h3>
        <ol>
          <li>Select your desired squad size (2-50 players)</li>
          <li>Choose a playstyle (balanced, offensive, defensive, etc.)</li>
          <li>
            Let the tool suggest an optimal composition, or build your own
          </li>
          <li>Fine-tune roles and professions to match your group's needs</li>
          <li>Save and share your composition with others</li>
        </ol>

        <h3>Contribute</h3>
        <p>
          GW2 WvW Builder is an open-source project. We welcome contributions
          from the community! Whether you're a developer, designer, or GW2
          enthusiast, there are many ways to help improve the tool.
        </p>

        <div className="mt-8 flex gap-4">
          <Button asChild>
            <a
              href="https://github.com/yourusername/gw2-wvwbuilder"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/builder">Try the Builder</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
