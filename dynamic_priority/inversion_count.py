def merge_and_count_inversions(outputs, data_tensor, temp, left, mid, right):
    i = left
    j = mid + 1
    k = left
    inv_count = 0

    while i <= mid and j <= right:
        if outputs[i] > outputs[j] and (data_tensor[i][0] < data_tensor[j][0] and data_tensor[i][1] < data_tensor[j][1]):
            inv_count += (mid - i + 1)
            j += 1
        else:
            i += 1

    i = left
    j = mid + 1
    k = left

    while i <= mid and j <= right:
        if outputs[i] <= outputs[j]:
            temp[k] = outputs[i]
            k += 1
            i += 1
        else:
            temp[k] = outputs[j]
            k += 1
            j += 1

    while i <= mid:
        temp[k] = outputs[i]
        k += 1
        i += 1

    while j <= right:
        temp[k] = outputs[j]
        k += 1
        j += 1

    for l in range(left, right + 1):
        outputs[l] = temp[l]

    return inv_count

def merge_sort_and_count_inversions(outputs, data_tensor, temp, left, right):
    inv_count = 0
    if left < right:
        mid = (left + right) // 2
        inv_count += merge_sort_and_count_inversions(outputs, data_tensor, temp, left, mid)
        inv_count += merge_sort_and_count_inversions(outputs, data_tensor, temp, mid + 1, right)
        inv_count += merge_and_count_inversions(outputs, data_tensor, temp, left, mid, right)
    return inv_count


if __name__ == "__main__":

    # 示例
    outputs = [8, 4, 2, 1, 3, 7, 6, 5]
    data_tensor = [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9]]
    temp = [0] * len(outputs)
    inverse_pairs = merge_sort_and_count_inversions(outputs, data_tensor, temp, 0, len(outputs) - 1)
    print("Number of inverse pairs:", inverse_pairs)

    inverse_pairs = merge_sort_and_count_inversions(outputs, data_tensor, temp, 0, len(outputs) - 1)
    print("Number of inverse pairs:", inverse_pairs)