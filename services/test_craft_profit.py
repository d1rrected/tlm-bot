import math

def craft_cost(initial_craft_count, mat_1_price, mat_1_per_item, mat_2_price, mat_2_per_item, artifact_price, return_percent, craft_price):
    total_materials_1 = initial_craft_count * mat_1_per_item
    total_materials_2 = initial_craft_count * mat_2_per_item
    total_artifacts = initial_craft_count if artifact_price > 0 else 0

    actual_craft_count = 0
    need_artifacts = initial_craft_count
    while total_materials_1 >= mat_1_per_item and (total_materials_2 >= mat_2_per_item or mat_2_price == 0):
        actual_craft_count += 1
        total_materials_1 -= mat_1_per_item
        total_materials_2 -= mat_2_per_item
             
        total_materials_1 += math.floor(mat_1_per_item * return_percent)
        total_materials_2 += math.floor(mat_2_per_item * return_percent)
    
    remaining_materials_cost = (total_materials_1 * mat_1_price) + (total_materials_2 * mat_2_price) 
    cost_of_result = actual_craft_count * craft_price
    materials_cost = (mat_1_price * mat_1_per_item + mat_2_price * mat_2_per_item + artifact_price) * initial_craft_count
    
    print(f"You need {actual_craft_count} artifacts.")
    print(f"Cost of materials: res={materials_cost} + art={(actual_craft_count * artifact_price)}; Cost of crafted items: {cost_of_result}, Total Profit: {cost_of_result - materials_cost - (actual_craft_count * artifact_price) + remaining_materials_cost}")

    return remaining_materials_cost, cost_of_result

# Пример использования
remaining, result_cost = craft_cost(20, 20000, 16, 0, 0, 140000, 0.401, 394000)
print(f"Reaimning resources price: {remaining}. Result cost: {result_cost}")
