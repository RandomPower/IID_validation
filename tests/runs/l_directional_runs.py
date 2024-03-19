""" 5.1.3 Lenght of Directional Runs"""

def l_directional_runs(S):
    S_prime = []
    for i in range(0, len(S) - 1):
        if S[i] > S[i + 1]:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0
    # S_prime should be len(S) - 1

    T = 0
    current_count = 1  # Initialize with 1 for the first item

    for k in range(0, len(S_prime) - 1):
        if S_prime[k] == S_prime[k + 1]:
            current_count += 1
        else:
            if current_count > T:
                T = current_count
                current_count = 1

    # Check one more time after the loop for the last sequence
    if current_count > T:
        T = current_count

    # return max_count
    return T


'''S = [10,9,8,7,6,5,4,25,23,4,5,6]

T = l_directional_runs(S)
print(T)'''