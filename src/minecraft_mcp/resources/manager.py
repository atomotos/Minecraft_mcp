from typing import Dict, Any, List, Optional, Union
from minecraft_mcp.models.player import PlayerInventory
from minecraft_mcp.models.blueprint import ArchitecturalBlueprint
from minecraft_mcp.models.construction import ConstructionPlan
from minecraft_mcp.models.resources import (
    ResourceRequirement,
    ResourceStatus,
    CraftingRecipe,
    CraftingStep,
)
from minecraft_mcp.construction.compiler import BlueprintCompiler

# ---------------------------------------------------------------------------
# Standard Vanilla Crafting Knowledge
# ---------------------------------------------------------------------------

DEFAULT_CRAFTING_RECIPES: List[CraftingRecipe] = [
    CraftingRecipe(recipe_id="oak_log_to_planks", output_item="minecraft:oak_planks", output_count=4, inputs={"minecraft:oak_log": 1}),
    CraftingRecipe(recipe_id="spruce_log_to_planks", output_item="minecraft:spruce_planks", output_count=4, inputs={"minecraft:spruce_log": 1}),
    CraftingRecipe(recipe_id="birch_log_to_planks", output_item="minecraft:birch_planks", output_count=4, inputs={"minecraft:birch_log": 1}),
    CraftingRecipe(recipe_id="planks_to_stairs", output_item="minecraft:oak_stairs", output_count=4, inputs={"minecraft:oak_planks": 6}),
    CraftingRecipe(recipe_id="planks_to_slabs", output_item="minecraft:oak_slab", output_count=6, inputs={"minecraft:oak_planks": 3}),
    CraftingRecipe(recipe_id="planks_to_door", output_item="minecraft:oak_door", output_count=3, inputs={"minecraft:oak_planks": 6}),
    CraftingRecipe(recipe_id="planks_to_table", output_item="minecraft:crafting_table", output_count=1, inputs={"minecraft:oak_planks": 4}),
    CraftingRecipe(recipe_id="planks_to_sticks", output_item="minecraft:stick", output_count=4, inputs={"minecraft:oak_planks": 2}),
    CraftingRecipe(recipe_id="sticks_and_planks_to_fence", output_item="minecraft:oak_fence", output_count=3, inputs={"minecraft:oak_planks": 4, "minecraft:stick": 2}),
    CraftingRecipe(recipe_id="cobblestone_to_stone_bricks", output_item="minecraft:stone_bricks", output_count=4, inputs={"minecraft:cobblestone": 4}),
    CraftingRecipe(recipe_id="cobblestone_to_furnace", output_item="minecraft:furnace", output_count=1, inputs={"minecraft:cobblestone": 8}),
    CraftingRecipe(recipe_id="stone_to_stairs", output_item="minecraft:stone_brick_stairs", output_count=4, inputs={"minecraft:stone_bricks": 6}),
    CraftingRecipe(recipe_id="stone_to_wall", output_item="minecraft:stone_brick_wall", output_count=6, inputs={"minecraft:stone_bricks": 6}),
    CraftingRecipe(recipe_id="glass_to_pane", output_item="minecraft:glass_pane", output_count=16, inputs={"minecraft:glass": 6}),
]

class ResourceManager:
    def __init__(self, recipes: Optional[List[CraftingRecipe]] = None):
        self.recipes = recipes or DEFAULT_CRAFTING_RECIPES

    def get_inventory_counts(self, inventory: PlayerInventory) -> Dict[str, int]:
        """Aggregates all item counts across hotbar, main inventory, and offhand."""
        counts: Dict[str, int] = {}
        all_slots = (inventory.hotbar or []) + (inventory.main or []) + ([inventory.offhand] if inventory.offhand else [])
        for slot in all_slots:
            if not slot or slot.count <= 0:
                continue
            raw_id = getattr(slot, "id", None) or getattr(slot, "item", None)
            if raw_id:
                item_id = raw_id.split("[")[0]
                if ":" not in item_id:
                    item_id = f"minecraft:{item_id}"
                counts[item_id] = counts.get(item_id, 0) + slot.count
        return counts

    def check_requirements(
        self,
        blueprint_or_plan: Union[str, ArchitecturalBlueprint, ConstructionPlan, Dict[str, Any]],
        inventory: PlayerInventory,
        anchor: Optional[Dict[str, int]] = None
    ) -> ResourceRequirement:
        """
        Calculates material requirements, compares against inventory,
        and solves crafting possibilities for missing materials.
        """
        # Obtain materials required dict
        if isinstance(blueprint_or_plan, ConstructionPlan):
            required = blueprint_or_plan.materials_required
        else:
            ref_anchor = anchor or {"x": 0, "y": 64, "z": 0}
            plan = BlueprintCompiler.compile(blueprint_or_plan, ref_anchor)
            required = plan.materials_required

        available = self.get_inventory_counts(inventory)
        missing: Dict[str, int] = {}

        for item_id, count_needed in required.items():
            avail_count = available.get(item_id, 0)
            if avail_count < count_needed:
                missing[item_id] = count_needed - avail_count

        # If no missing materials, return SUFFICIENT
        if not missing:
            return ResourceRequirement(
                required=required,
                available=available,
                missing={},
                craftable=True,
                crafting_plan=[],
                status=ResourceStatus.SUFFICIENT,
            )

        # Evaluate crafting recovery
        crafting_plan: List[CraftingStep] = []
        can_craft = True
        temp_available = available.copy()

        for missing_item, deficit in missing.items():
            resolved = False
            # Look for recipes producing missing_item
            for recipe in self.recipes:
                if recipe.output_item == missing_item:
                    # Calculate how many times recipe must be crafted
                    times_needed = (deficit + recipe.output_count - 1) // recipe.output_count
                    # Check if all inputs are present in temp_available
                    has_all_inputs = True
                    for inp_item, inp_count in recipe.inputs.items():
                        req_inp = inp_count * times_needed
                        if temp_available.get(inp_item, 0) < req_inp:
                            has_all_inputs = False
                            break
                    if has_all_inputs:
                        # Deduct inputs and produce output
                        for inp_item, inp_count in recipe.inputs.items():
                            temp_available[inp_item] -= (inp_count * times_needed)
                        temp_available[missing_item] = temp_available.get(missing_item, 0) + (recipe.output_count * times_needed)
                        crafting_plan.append(CraftingStep(
                            recipe_id=recipe.recipe_id,
                            input_items={k: v * times_needed for k, v in recipe.inputs.items()},
                            output_item=recipe.output_item,
                            output_count=recipe.output_count * times_needed,
                        ))
                        resolved = True
                        break

            if not resolved:
                can_craft = False

        status = ResourceStatus.SHORTAGE if can_craft else ResourceStatus.UNOBTAINABLE
        return ResourceRequirement(
            required=required,
            available=available,
            missing=missing,
            craftable=can_craft,
            crafting_plan=crafting_plan,
            status=status,
        )
