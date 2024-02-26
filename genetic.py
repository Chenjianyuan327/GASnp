import numpy as np
import random
import pandas as pd
import time


def vcf_read(path):
    snp = []
    rows_name = []
    for line in open(path, 'r'):
        if line[:2] == '##':
            continue

        if line[0] == '#':
            cols_name = line.strip().split('\t')
            continue

        line = line.strip().split('\t')
        rows_name.append(line[:9])
        snp.append(line[9:])

    return np.array(snp).transpose(1, 0), cols_name, rows_name


def init_pop(l_snp, n_pop, l_pop):
    pop = np.empty((0, l_pop))
    while n_pop:
        _pop = np.array([random.sample(range(l_snp), l_pop) for _ in range(n_pop)])  # 初始化
        _pop = np.sort(_pop, axis=1)  # 基因序号排序

        pop = np.concatenate([pop, _pop], axis=0)
        pop = np.unique(pop, axis=0)  # 除去重复的个体

        n_pop = n_pop - pop.shape[0]

    return pop.astype(int)


def fit(pop, snp):
    fitness = np.array([np.unique(snp[:, pop_i], axis=0).shape[0] for pop_i in pop])

    return fitness


def selection(pop, fitness):
    prob = fitness / fitness.sum()  # 概率化, fitness越大越好
    p_cs = np.cumsum(prob)  # 累加概率

    # 轮盘赌选择法
    N = pop.shape[0] // 2 * 2  # 待选择的个体数
    pr = sorted([random.random() for i in range(N)])
    fitin, newin, sele_pop = 0, 0, []
    while newin < N:
        if (pr[newin] < p_cs[fitin]):
            sele_pop.append(pop[fitin])
            newin = newin + 1
        else:
            fitin = fitin + 1
    random.shuffle(sele_pop)

    # 父母划分
    father, mother = sele_pop[::2], sele_pop[1::2]
    return father, mother


def crossover(father, mother):
    son, l = [], father[0].shape[0]
    for i in range(len(father)):
        ind = np.random.randint(0, 2, l).astype(bool)  # 随机选择交叉的点位
        son1 = father[i].copy()
        son2 = mother[i].copy()

        son1[ind] = mother[i][ind]
        son2[ind] = father[i][ind]
        son.extend([son1, son2])

    return son


def mutation(_son, pm, l_snp):
    son, l = [], _son[0].shape[0]
    for sn in _son:
        if random.random() < pm:  # 变异
            ind = np.random.choice(a=range(l), size=int(pm * l), replace=False)
            sn[ind] = random.sample(range(l_snp), len(ind))

        # 除去重复基因
        lost = l - np.unique(sn).shape[0]
        if lost > 0:
            gene = random.sample(set(range(l_snp)).difference(sn), lost)
            sn.sort()
            ind = [i for i in range(sn.shape[0] - 1) if sn[i + 1] == sn[i]]
            sn[ind] = gene

        son.append(sn)
    son = np.stack(son)
    return np.sort(son, axis=1)


def update(pop, son, fitness, snp):
    N = pop.shape[0]
    # 计算子代的适应度
    son_fitness = fit(son, snp)

    # 父代和子代合并
    new_pop = np.concatenate([pop, son])
    new_fitness = np.concatenate([fitness, son_fitness])

    # 除去重复个体
    new_pop, ind = np.unique(new_pop, return_index=True, axis=0)
    new_fitness = new_fitness[ind]

    # 适应度排序，淘汰旧个体
    pop_fitness = list(zip(new_fitness, new_pop))
    pop_fitness = sorted(pop_fitness, key=lambda x: x[0], reverse=True)
    fitness, pop = zip(*pop_fitness)

    return np.array(pop[:N]), np.array(fitness[:N])


'''
def plot_print(i, log_fit_mean, log_fit_max):
    print('epoch: {} best_fit: {}'.format(i + 1, log_fit_max[-1]))

    # 实时显示迭代曲线
    plt.clf()  # 清空画布上的所有内容
    plt.plot(log_fit_mean, label="fitness_mean", color='g', linewidth=3)
    plt.plot(log_fit_max, label='fitness_max', color='r', linewidth=3)
    plt.xlabel('epoch')
    plt.ylabel('fitness')
    plt.legend()
    plt.draw()
    plt.pause(0.01)
'''


def save2excel(vcf, best_snp, cols_name, rows_name, fit_mean, fit_max):
    # 原始数据行列的id
    cols_id, rows_id = list(range(vcf.shape[0]+9)), list(range(vcf.shape[1]+1))

    # 最佳个体对应的基因位置(id)
    best_rows_id = rows_id[:1] + [rows_id[i+1] for i in best_snp]
    best_rows_name = np.array([rows_name[i] for i in best_snp])

    # 能够被识别的基因片段, 及个体名称
    gene, ind = np.unique(vcf[:, best_snp], axis=0, return_index=True)
    inds = np.argsort(ind)  # 排序
    gene, ind = gene[inds], ind[inds]
    best_gene = gene.transpose(1, 0)

    best_cols_id = cols_id[:9] + [cols_id[i+9] for i in ind]
    best_cols_name = np.array(cols_name[:9] + [cols_name[i+9] for i in ind]).reshape(1, -1)

    # 行列合并
    res = np.concatenate([best_rows_name, best_gene], axis=1)
    res = np.concatenate([best_cols_name, res], axis=0)

    # 存为excel
    save_name = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))+'.xlsx'

    df1 = pd.DataFrame(res, index=best_rows_id, columns=best_cols_id)  #
    df2 = pd.DataFrame(np.array([fit_mean, fit_max]).transpose(1, 0), columns=['fit_mean', 'fit_max'])
    with pd.ExcelWriter(save_name) as writer:
        df1.to_excel(writer, sheet_name='Sheet1')
        df2.to_excel(writer, sheet_name='Sheet2')

    return save_name


def genetic(path, n_pop=50, epoch=1000, l_pop=80, pm=0.3):
    vcf, cols_name, rows_name = vcf_read(path)

    pop = init_pop(vcf.shape[1], n_pop, l_pop)  # 种群初始化
    fitness = fit(pop, vcf)  # 计算适应度

    log_fit_mean, log_fit_max = [fitness.mean()], [fitness.max()]  # 记录平均适应度和最佳适应度
    for i in range(epoch):
        father, mother = selection(pop, fitness)  # 选择优秀父代
        son = crossover(father, mother)  # 交叉产生后代
        son = mutation(son, pm, vcf.shape[1])  # 后代变异
        pop, fitness = update(pop, son, fitness, vcf)  # 种群更新

        log_fit_mean.append(fitness.mean())
        log_fit_max.append(fitness.max())

        # 日志打印与显示
        # plot_print(i, log_fit_mean, log_fit_max)

        if log_fit_max[-1] == vcf.shape[0]:  # 找到最优, 提前结束
            save_name = save2excel(vcf, pop[0], cols_name, rows_name, log_fit_mean, log_fit_max)
            return save_name, log_fit_max[0]

    save_name = save2excel(vcf, pop[0], cols_name, rows_name, log_fit_mean, log_fit_max)
    return save_name, log_fit_max[0]


if __name__ == "__main__":
    genetic('data/part2.vcf', n_pop=50, epoch=10, l_pop=20, pm=0.3)
