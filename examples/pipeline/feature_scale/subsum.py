def subsum(a:list) -> int:
    if len(a) == 1:
        return a[0]
    l = len(a)
    sum = [0 for i in range(l)]
    sum[0] = a[0]
    max = sum[0]
    for i in range(1,l):
        sum[i] = sum[i-1]+a[i] if sum[i-1]+a[i]>a[i] else a[i]
        max = max if max>sum[i] else sum[i]
    return max

if __name__ == "__main__":
    a = [34,-3,8,23,-23,29]
    print(subsum(a))