from typing import List, Tuple, Dictn

def calculate_work_durations(works: List[Tuple[int, str, int, int]]) -> Dict[str, int]:
    durations = {
        'shift': 0,
        'repairing': 0,
        'moonlighting': 0
    }
    
    for work in works:
        _, work_type, duration, _ = work
        if work_type in durations:
            durations[work_type] += duration

    return durations

def calculate_total_expenses_payment(expenses: List[Tuple[int, int, int, int]]) -> int:
    total_expenses = 0  # Инициализируем переменную для хранения общей суммы

    for expense in expenses:
        _, payment, _ = expense
        total_expenses += payment  # Добавляем значение платежа к общей сумме

    return total_expenses  # Возвращаем итоговую сумму

def calculate_work_costs(
    works: List[Tuple[int, str, int, int]], 
    settings: Tuple[int, int, int, int, int]
) -> Dict[str, int]:
    _, shift_hour_rate, repairing_hour_rate, moonlighting_hour_rate, meal_compensation = settings
    
    # Инициализация суммарных значений и сумм
    total_shift_hours = 0
    total_repairing_hours = 0
    total_moonlighting_hours = 0
    
    total_cost_shift = 0
    total_cost_repairing = 0
    total_cost_moonlighting = 0
    
    # Обработка каждого типа работы
    for work in works:
        _, work_type, duration, _ = work
        
        if work_type == 'Смена':
            total_shift_hours += duration
            total_cost_shift += duration * shift_hour_rate
        elif work_type == 'Подработка':
            total_repairing_hours += duration
            total_cost_repairing += duration * repairing_hour_rate
        elif work_type == 'Ремонт':
            total_moonlighting_hours += duration
            total_cost_moonlighting += duration * moonlighting_hour_rate
    
    # Учет ограничений на часы ремонта
    if total_moonlighting_hours > 33:
        excess_moonlighting_hours = total_moonlighting_hours - 33
        total_moonlighting_hours = 33
        total_shift_hours += excess_moonlighting_hours
        total_cost_shift += excess_moonlighting_hours * shift_hour_rate
    
    # Общая стоимость
    overall_total_cost = total_cost_shift + total_cost_repairing + total_cost_moonlighting
    
    return {
        'shift_hours': total_shift_hours, # общее количество часов смен
        'repairing_hours': total_repairing_hours, # общее количество часов подработки
        'moonlighting_hours': total_moonlighting_hours, # общее количество часов ремонта
        'shift_cost': total_cost_shift, # начислена за отработанные часы смен
        'repairing_cost': total_cost_repairing, # начислена за отработанные часы подработки
        'moonlighting_cost': total_cost_moonlighting, # начислена за отработанные часы ремонта
        'total_cost': overall_total_cost, # общий заработок вообще за ремонты, подработку и смены
        'meal_compensation': meal_compensation # денежная компенсация за питание
    }