import numpy as np
from simulate import simulate
import multiprocessing as mp

shuffled_pollution_activate = False

if __name__ ==  '__main__': 
    
    #infection_rate = (0.0, 0.25, 50)
    #tile_rate = (0.0, 0.25, 50)
    infection_rate = (0.0, 0.25, 2)
    tile_rate = (0.0, 0.25, 2)

    inf_rate_size = infection_rate[2]
    tile_rate_size = tile_rate[2]
    inf = np.linspace(infection_rate[0], infection_rate[1], infection_rate[2])
    tile_inf = np.linspace(tile_rate[0], tile_rate[1], tile_rate[2])

    Lx = 30
    Ly = 30
    stepSize = 0.5
    N = 100
    N_ill = 1
    flow = 0
    realisations = 1
    tMax = 1000

    per = np.zeros(shape=(inf_rate_size, tile_rate_size), dtype=float)
    env = np.zeros(shape=(inf_rate_size, tile_rate_size), dtype=float)

    total_jobs = inf_rate_size * tile_rate_size
    last_inf = infection_rate[0]
    last_tile = tile_rate[0]
    last_row = 0
    last_col = 0

    for t in range(total_jobs):
        curr_row = int(t/(tile_rate_size))
        curr_col = t-int(t/(tile_rate_size))*(tile_rate_size)
        if not shuffled_pollution_activate:
            job = tuple([N, N_ill, Lx, Ly, stepSize, inf[curr_row], tile_inf[curr_col], tile_inf[curr_col], flow, tMax])
        elif shuffled_pollution_activate:
            job = tuple([N, N_ill, Lx, Ly, stepSize, inf[curr_row], tile_inf[curr_col], tile_inf[curr_col], flow, tMax, True])
        #job = 1,True, True
        works = [job for i in range(realisations)]
        with mp.Pool(mp.cpu_count()) as pool:
            p_r = pool.map_async(simulate, works)
            res = p_r.get()
        for i in range(len(res)):
            res[i] = (res[i]['from_per'].cumsum(), res[i]['from_env'].cumsum())
        ts = np.mean(res, axis=0)
        from_per = ts[0][-1]/job[0]
        from_env = ts[1][-1]/job[0]
        per[curr_row][curr_col] = from_per
        env[curr_row][curr_col] = from_env
    
    rand_id = str(np.random.randint(100000000))
    id_string = ', realizations=' + str(realisations) + ', ' + rand_id
    
    if shuffled_pollution_activate:
        id_string = ' sh_p, ' + id_string
    
    np.save('from_per' + id_string, per)
    np.save('from_env' + id_string, env)
    
    with open("info sweep " + rand_id, "w") as f: 
        f.write( 'parameter sweep:\n' )
        if shuffled_pollution_activate:
            f.write('shuffled\n')
        else:
            f.write('not shuffled\n')

        f.write('run number =' + realisations)
        f.write('tMax =' + tMax)
        f.write( 'infection_rate='+str( infection_rate ) + '\n' )
        f.write( 'tile_rate='+str( tile_rate ) + '\n' )
        f.write( str(job)[1:-1] )