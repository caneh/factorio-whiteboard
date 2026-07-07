--/sc

--[[
does not use ELSE output, works in version 2.0

how to use:
1) change the constants: minimum_items_desired, maximum_items_desired, ingredient_stock_multiplier
2) set the necessary recipes: local recipes = {}
3) select a decider-combinator in the game and run the script
4) select a constant-combinator in the game and run the script
5) use combinators in the build, see example BP
]]
--[[
    local quality = "legendary"
    local quality = "epic"
    local quality = "rare"
    local quality = "uncommon"
    local quality = "normal"]]
local minimum_items_desired = 1
local maximum_items_desired = 1
local ingredient_stock_multiplier = 1 --[[to start production you need this supply in chests]]

local recipes = {
    {name = "carbonic-asteroid-crushing", quality = "normal"},
    {name = "oxide-asteroid-crushing", quality = "normal"},
    {name = "metallic-asteroid-crushing", quality = "normal"}
}
local recipes = {
    {name = "biochamber", quality = "rare"},
    {name = "biochamber", quality = "epic"},
    {name = "biochamber", quality = "legendary"}
}

--[[-------------------------------------------------]]
local function add_recipe_conditions(recipe, combinator, quality, product_amount, ingr_stock_multiplier)
    for _, result in pairs(recipe.products) do
        combinator.add_condition {
            first_signal = {type = result.type, name = result.name, quality = quality},
            first_signal_networks = {red = false, green = true},
            constant = product_amount,
            comparator = "<",
            compare_type = "and"
        }
    end
    for _, ingredient in pairs(recipe.ingredients) do
        local ingredient_quality = ingredient.type == "item" and quality or "normal"
        local required_amount = ingredient.amount * ingr_stock_multiplier
        combinator.add_condition {
            first_signal = {type = ingredient.type, name = ingredient.name, quality = ingredient_quality},
            first_signal_networks = {red = false, green = true},
            constant = required_amount,
            comparator = ">=",
            compare_type = "and"
        }
    end
end

--[[-------------------------------------------------]]
local function make_everything_combinator_old(entity)
    if not entity then
        return
    end
    if entity.type == "decider-combinator" then
        local combinator = entity.get_control_behavior()
        combinator.parameters = {conditions = {}, outputs = {}}

        local index = -1
        for _, r in pairs(recipes) do
            local quality = r.quality
            local recipe = prototypes.recipe[r.name]
            index = index + 2
            --[[local stack_size = recipe.main_product and prototypes.item[recipe.main_product.name].stack_size or -1]]
            --[[section that starts recipe production]]
            combinator.add_condition {
                first_signal = {type = "virtual", name = "signal-each"},
                first_signal_networks = {green = false, red = true},
                constant = index,
                comparator = "="
            }
            combinator.add_condition {
                first_signal = {type = "virtual", name = "signal-deny"},
                first_signal_networks = {green = false, red = true},
                comparator = "=",
                compare_type = "and"
            }
            add_recipe_conditions(recipe, combinator, quality, minimum_items_desired, ingredient_stock_multiplier)
            --[[section that continues production of the recipe]]
            combinator.add_condition {
                first_signal = {type = "virtual", name = "signal-each"},
                first_signal_networks = {green = false, red = true},
                constant = index + 1,
                comparator = "="
            }
            add_recipe_conditions(recipe, combinator, quality, maximum_items_desired, 1)
        end
        --[[-------------------]]
        combinator.add_output(
            {
                signal = {type = "virtual", name = "signal-each"},
                constant = 1,
                copy_count_from_input = false
            }
        )
        combinator.add_output(
            {
                signal = {type = "virtual", name = "signal-deny"},
                constant = -1,
                copy_count_from_input = false
            }
        )
    end
    if entity.type == "constant-combinator" then
        --[[fill in the necessary constants]]
        local index = -1
        local combinator = entity.get_control_behavior()
        combinator.add_section()
        local section = combinator.get_section(1)
        local slot_index = 0
        for _, r in pairs(recipes) do
            local quality = r.quality
            local recipe = prototypes.recipe[r.name]
            index = index + 2
            slot_index = slot_index + 1
            section.set_slot(
                slot_index,
                {
                    value = {type = "recipe", name = recipe.name, quality = quality},
                    min = index
                }
            )
        end
    end
end

make_everything_combinator_old(game.player.selected)
