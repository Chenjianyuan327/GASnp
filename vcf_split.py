
with open(r'C:\Users\sk\Desktop\part2.vcf', 'w') as fid:
    for i, line in enumerate(open(r'C:\Users\sk\Desktop\test.vcf', 'r')):
        fid.write(line)

        if i >= 10000:
            break