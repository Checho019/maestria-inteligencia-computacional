%% Taller 2: Redes Neuronales Multicapa (MLP) y Backpropagation
% *Asignatura:* Inteligencia Computacional Aplicada
%
% *Docente:* Cesar Andrey Perdomo Charry
%
% *Estudiante:* Sergio Santiago Duarte Rojas
%% 1. Fundamento teórico: Perceptrón Multicapa (MLP) y Backpropagation
% *¿Por qué una sola capa no basta?* En el Taller 1 vimos que el Perceptrón
% Simple y Adaline solo pueden resolver problemas *linealmente separables*. El
% problema XOR es el ejemplo clásico de un problema que *no* lo es, y por eso
% requiere una arquitectura con al menos una *capa oculta*.
%
% *Arquitectura del MLP*
%
% Una red multicapa se organiza en capas $k = 1,\dots,L$. Cada neurona $j$ de
% la capa $k$ calcula:
%
% $$net_j^{(k)} = \sum_i w_{ji}^{(k)} a_i^{(k-1)} + b_j^{(k)}, \qquad a_j^{(k)}
% = f\left(net_j^{(k)}\right)$$
%
% donde $a^{(0)} = x$ (la entrada) y $f$ es la función de activación de la capa
% (sigmoidal, tangente hiperbólica o ReLU en este taller).
%
% *Algoritmo de Backpropagation*
%
% El error se mide típicamente como error cuadrático medio:
%
% $$E = \frac{1}{2}\sum \left(d(x) - Y(x)\right)^2$$
%
% El algoritmo ajusta los pesos por *descenso de gradiente*, propagando el error
% desde la salida hacia las capas ocultas:
%
% $$\delta^{(L)} = \left(d(x) - Y(x)\right) \odot f'\left(net^{(L)}\right) \qquad
% \text{(capa de salida)}$$
%
% $$\delta^{(k)} = \left(W^{(k+1)T}\delta^{(k+1)}\right) \odot f'\left(net^{(k)}\right)
% \qquad \text{(capas ocultas)}$$
%
% $$W^{(k)} \leftarrow W^{(k)} + \eta\, \delta^{(k)} \left(a^{(k-1)}\right)^T,
% \qquad b^{(k)} \leftarrow b^{(k)} + \eta\, \delta^{(k)}$$
%
% donde $\eta$ es la tasa de aprendizaje. Opcionalmente se agrega un *término
% de momento* $\beta$ que suaviza la trayectoria de convergencia usando el incremento
% de la iteración anterior:
%
% $$\Delta W^{(k)} \leftarrow \eta\, \delta^{(k)} \left(a^{(k-1)}\right)^T +
% \beta\, \Delta W^{(k)}_{\text{anterior}}$$
%
% *Funciones de activación más comunes*
%%
% * *Sigmoidal:* $f(net)=\dfrac{1}{1+e^{-net}}$, con $f'(net)=f(net)(1-f(net))$.
% Satura para valores extremos, lo que puede ralentizar el aprendizaje (_vanishing
% gradient_).
% * *Tangente hiperbólica:* $f(net)=\tanh(net)$, con $f'(net)=1-\tanh^2(net)$.
% Centrada en cero, suele converger algo más rápido que la sigmoidal.
% * *ReLU:* $f(net)=\max(0,net)$, con $f'(net)=1$ si $net>0$ y $0$ en caso contrario.
% Evita la saturación pero puede "apagar" neuronas (_dying ReLU_).
%%
% *Referencias y lecturas complementarias*
%%
% * Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning representations
% by back-propagating errors. _Nature_, 323(6088), 533-536.  <https://doi.org/10.1038/323533a0
% doi.org/10.1038/323533a0>
% * Haykin, S. (2009). _Neural Networks and Learning Machines_ (3rd ed.), Capítulo
% 4: Multilayer Perceptrons. Pearson.
% * Goodfellow, I., Bengio, Y., & Courville, A. (2016). _Deep Learning_, Capítulo
% 6. <https://www.deeplearningbook.org/ deeplearningbook.org> (disponible gratis
% en línea)
% * Nielsen, M. (2015). _Neural Networks and Deep Learning_, Capítulo 2 (backpropagation,
% con derivación paso a paso).  <http://neuralnetworksanddeeplearning.com/chap2.html
% neuralnetworksanddeeplearning.com/chap2.html> (libro gratuito en línea)
% * MathWorks. <https://www.mathworks.com/help/deeplearning/ug/multilayer-shallow-neural-networks-and-backpropagation-training.html
% Multilayer Shallow Neural Networks and Backpropagation Training>

clear; clc; close all;
%% 2. Parámetros del modelo (totalmente parametrizable)
% *Qué se espera en esta sección:* una estructura |cfg| editable que controla
% la arquitectura de la red y el proceso de entrenamiento. No requiere que complete
% código aquí, pero *sí* deberá modificar estos valores (número de neuronas ocultas,
% función de activación, tasa de aprendizaje, etc.) en los distintos numerales
% del taller para comparar arquitecturas.
%
% Se agregan a |cfg| el criterio de parada por épocas sin mejora (|patience|),
% el umbral de decisión, la fracción de validación, la escala de los pesos
% iniciales y las rutas de los datos. |act_hidden| acepta una celda con una
% activación por capa oculta. Las tablas de resultados de los numerales 3 a 6
% se acumulan en |R3| a |R6|.

cfg.n_inputs      = 2;            % número de entradas
cfg.hidden_layers = [4];          % neuronas por capa oculta, ej. [4 3]
cfg.n_outputs     = 1;            % número de salidas
cfg.act_hidden    = 'sigmoid';    % 'sigmoid' | 'tanh' | 'relu'
cfg.act_output    = 'sigmoid';    % 'sigmoid' | 'tanh' | 'relu' | 'linear'
cfg.eta           = 0.3;          % tasa de aprendizaje (eta)
cfg.momentum      = 0.0;          % coeficiente de momento (beta), 0-1
cfg.max_epochs    = 5000;
cfg.target_error  = 1e-3;
cfg.patience      = 0;            % épocas sin mejora en validación antes de parar, 0 desactiva
cfg.threshold     = 0.5;          % umbral de decisión con una sola salida
cfg.val_fraction  = 0.2;          % parte del entrenamiento que se reserva para validación
cfg.init_scale    = 0.5;          % escala de los pesos iniciales, W = randn * init_scale
cfg.seed          = 1;
cfg.datos         = struct('iris', 'iris.dat', 'wine', 'wine.data', 'wdbc', 'wdbc.data', ...
                           'banknote', 'data_banknote_authentication.txt');
cfg_base = cfg;

paleta = [0.00 0.35 0.64; 0.85 0.37 0.01; 0.00 0.55 0.40; 0.45 0.20 0.55; 0.80 0.65 0.10; 0.40 0.45 0.50];

rng(cfg.seed);
%% 3. Datos de entrenamiento
% *Teoría breve:* el problema XOR asigna salida 1 cuando exactamente una de
% las dos entradas es 1, y 0 en caso contrario. No existe una única línea recta
% (hiperplano) que separe las clases, por lo que un Perceptrón simple (Taller
% 1) *no puede* resolverlo; de ahí la necesidad de la capa oculta.
%
% *Qué se espera en esta sección:* las matrices |X| (patrones, una fila por
% patrón) y |D| (salidas deseadas) listas para entrenar.

X = [0 0; 0 1; 1 0; 1 1];   % cada FILA es un patrón de entrada
D = [0; 1; 1; 0];           % salida deseada d(x)
%% 4. Inicialización de la red — función |init_mlp|
% *Teoría:* los pesos se inicializan con valores aleatorios *pequeños* (no en
% cero) para romper la simetría entre neuronas de una misma capa; si todas partieran
% del mismo valor, aprenderían siempre lo mismo. Los sesgos (bias) usualmente
% se inicializan en cero.
%
% *Qué se espera en esta sección:* la función debe devolver una estructura |net|
% con:
%%
% * |net.W{k}| : matriz de pesos de la capa $k$ (tamaño: neuronas_k x neuronas_{k-1})
% * |net.b{k}| : vector de sesgos de la capa $k$
% * |net.dW_prev{k}|, |net.db_prev{k}| : incrementos anteriores en ceros, para
% el término de momento

net = init_mlp(cfg);
%% 5. Propagación hacia adelante — función |forward_mlp|
% *Teoría:* dado un patrón de entrada, se calcula la salida de cada capa aplicando
% la fórmula $a^{(k)} = f\left(W^{(k)}a^{(k-1)}+b^{(k)}\right)$ de manera secuencial
% hasta llegar a la capa de salida.
%
% *Qué se espera en esta sección:* la función debe devolver la salida |y| de
% la red y una estructura |cache| con los valores intermedios (|cache.a| y |cache.netv|
% de cada capa), necesarios para el paso de backpropagation.
%% 6. Retropropagación del error — función |backward_mlp|
% *Teoría:* implemente las fórmulas de la Sección 1 (deltas de salida y de las
% capas ocultas, y la actualización de pesos con momento opcional).
%
% *Qué se espera en esta sección:* la función debe actualizar y devolver |net|
% con los pesos ya ajustados para el patrón actual.
%% 7. Funciones de activación y sus derivadas
% *Qué se espera en esta sección:* |activation| ya está completa; usted debe
% completar |activation_deriv|, que se usa dentro de |backward_mlp| para calcular
% $f'(net)$.
%% 8. Entrenamiento (ciclo de épocas)
% *Teoría:* en el *aprendizaje en línea* (_online_), los pesos se actualizan
% patrón por patrón (a diferencia del aprendizaje por lotes, donde se acumula
% el gradiente de todo el conjunto antes de actualizar). Se recorre el conjunto
% de entrenamiento en orden aleatorio en cada época para evitar sesgos de orden.
%
% *Qué se espera en esta sección:* al ejecutar este bloque, el error cuadrático
% medio (|error_hist|) debe decrecer época a época hasta alcanzar |cfg.target_error|
% o completar |cfg.max_epochs|. Si el error no baja, revise las fórmulas completadas
% en las secciones 4-7.

error_hist = zeros(cfg.max_epochs, 1);

for epoch = 1:cfg.max_epochs
    epoch_error = 0;
    idx = randperm(size(X, 1));

    for p = idx
        x = X(p, :)';
        d = D(p, :)';

        % ---- forward pass ----
        [y, cache] = forward_mlp(net, x, cfg);

        % ---- backward pass (backpropagation) + actualización ----
        net = backward_mlp(net, cache, x, d, cfg);

        epoch_error = epoch_error + 0.5 * sum((d - y).^2);
    end

    error_hist(epoch) = epoch_error / size(X, 1);

    if error_hist(epoch) <= cfg.target_error
        fprintf('Convergencia en la época %d (error = %.6f)\n', epoch, error_hist(epoch));
        error_hist = error_hist(1:epoch);
        break;
    end
end
%% 9. Resultados y visualización
% *Qué se espera en esta sección:* una curva de error decreciente y, para el
% caso XOR, salidas cercanas a 0 o 1 que coincidan con la columna |d| para cada
% patrón. Compare estos resultados con los obtenidos en el Taller 1 (Perceptrón/Adaline)
% para el mismo problema: allí el modelo *no* debía poder converger en XOR.

figure;
plot(error_hist, 'LineWidth', 1.4);
xlabel('Época'); ylabel('Error cuadrático medio');
title('Curva de error de entrenamiento');
grid on;

fprintf('\nResultados finales:\n');
for p = 1:size(X, 1)
    y = forward_mlp(net, X(p, :)', cfg);
    fprintf('x = [%s]  ->  y = %.4f   (d = %g)\n', num2str(X(p, :)), y, D(p, :));
end
%% 9.1 Numeral 3, XOR de 2 y 3 entradas frente al Perceptrón y el Adaline del Taller 1
% La XOR de 3 entradas vale 1 cuando un número impar de entradas vale 1. Se
% entrena el MLP con tres tamaños de capa oculta y se repite con cinco semillas.
% El Perceptrón y el Adaline usan las mismas funciones del Taller 1.

cfgP = struct('threshold', 0.5, 'learning_rule', 'perceptron_alpha', 'alpha', 0.1, ...
              'max_epochs', 100, 'init_scale', 0.5, 'n_inputs', 2, 'seed', 1);
cfgA = struct('threshold', 0.5, 'alpha', 0.05, 'max_epochs', 200, 'target_mse', 1e-3, ...
              'init_scale', 0.5, 'n_inputs', 2, 'seed', 1);
semillas = 1:5;
ocultas_xor = {[2], [4], [8]};
R3 = table();
for n_in = [2 3]
    [X, D] = xor_data(n_in);
    cfgP.n_inputs = n_in;  cfgA.n_inputs = n_in;
    ep = zeros(numel(semillas), 1);  acc = ep;
    for s = semillas
        rng(s);  [W, b, ep(s)] = train_perceptron(X, D, cfgP);
        acc(s) = accuracy_of(X, D, W, b, cfgP.threshold);
    end
    R3 = [R3; table(n_in, {'Perceptrón'}, {'ninguna'}, mean(ep), 100*mean(ep < cfgP.max_epochs), mean(acc), ...
          'VariableNames', {'Entradas', 'Modelo', 'Ocultas', 'Epocas', 'Convergio', 'Exactitud'})];
    for s = semillas
        rng(s);  [W, b, mse_hist] = train_adaline(X, D, cfgA);
        ep(s) = numel(mse_hist);  acc(s) = accuracy_of(X, D, W, b, cfgA.threshold);
    end
    R3 = [R3; table(n_in, {'Adaline'}, {'ninguna'}, mean(ep), 100*mean(ep < cfgA.max_epochs), mean(acc), ...
          'VariableNames', {'Entradas', 'Modelo', 'Ocultas', 'Epocas', 'Convergio', 'Exactitud'})];
    for h = 1:numel(ocultas_xor)
        cfg = cfg_base;  cfg.n_inputs = n_in;  cfg.hidden_layers = ocultas_xor{h};
        for s = semillas
            cfg.seed = s;
            [net, hist] = train_mlp(X, D, [], [], cfg);
            ep(s) = hist.epochs;  acc(s) = accuracy_mlp(net, X, D, cfg);
        end
        R3 = [R3; table(n_in, {'MLP'}, {mat2str(ocultas_xor{h})}, mean(ep), 100*mean(ep < cfg.max_epochs), mean(acc), ...
              'VariableNames', {'Entradas', 'Modelo', 'Ocultas', 'Epocas', 'Convergio', 'Exactitud'})];
    end
    cfg = cfg_base;  cfg.n_inputs = n_in;  cfg.hidden_layers = [4];  cfg.momentum = 0.9;
    for s = semillas
        cfg.seed = s;  [net, hist] = train_mlp(X, D, [], [], cfg);
        ep(s) = hist.epochs;  acc(s) = accuracy_mlp(net, X, D, cfg);
    end
    R3 = [R3; table(n_in, {'MLP, momento 0.9'}, {'4'}, mean(ep), 100*mean(ep < cfg.max_epochs), mean(acc), ...
          'VariableNames', {'Entradas', 'Modelo', 'Ocultas', 'Epocas', 'Convergio', 'Exactitud'})];
end
cfg = cfg_base;
R3
%% 9.2 Momento y función de activación sobre la XOR
% Con cuatro neuronas ocultas se varía el coeficiente de momento y la función
% de activación de la capa oculta, cinco semillas por configuración. La última
% fila de cada bloque usa dos capas ocultas con una activación distinta en cada una.

momentos = [0 0.5 0.9];
activaciones = {'sigmoid', 'tanh', 'relu'};
R3b = table();
for n_in = [2 3]
    [X, D] = xor_data(n_in);
    for m = momentos
        cfg = cfg_base;  cfg.n_inputs = n_in;  cfg.hidden_layers = [4];  cfg.momentum = m;
        ep = zeros(numel(semillas), 1);  acc = ep;
        for s = semillas
            cfg.seed = s;  [net, hist] = train_mlp(X, D, [], [], cfg);
            ep(s) = hist.epochs;  acc(s) = accuracy_mlp(net, X, D, cfg);
        end
        R3b = [R3b; table(n_in, {'sigmoid'}, m, mean(ep), 100*mean(ep < cfg.max_epochs), mean(acc), ...
               'VariableNames', {'Entradas', 'Activacion', 'Momento', 'Epocas', 'Convergio', 'Exactitud'})];
    end
    for a = 2:3
        cfg = cfg_base;  cfg.n_inputs = n_in;  cfg.hidden_layers = [4];  cfg.act_hidden = activaciones{a};
        ep = zeros(numel(semillas), 1);  acc = ep;
        for s = semillas
            cfg.seed = s;  [net, hist] = train_mlp(X, D, [], [], cfg);
            ep(s) = hist.epochs;  acc(s) = accuracy_mlp(net, X, D, cfg);
        end
        R3b = [R3b; table(n_in, activaciones(a), 0, mean(ep), 100*mean(ep < cfg.max_epochs), mean(acc), ...
               'VariableNames', {'Entradas', 'Activacion', 'Momento', 'Epocas', 'Convergio', 'Exactitud'})];
    end
    cfg = cfg_base;  cfg.n_inputs = n_in;  cfg.hidden_layers = [4 4];  cfg.act_hidden = {'tanh', 'sigmoid'};  cfg.momentum = 0.9;
    ep = zeros(numel(semillas), 1);  acc = ep;
    for s = semillas
        cfg.seed = s;  [net, hist] = train_mlp(X, D, [], [], cfg);
        ep(s) = hist.epochs;  acc(s) = accuracy_mlp(net, X, D, cfg);
    end
    R3b = [R3b; table(n_in, {'[4 4], tanh y sigmoid'}, 0.9, mean(ep), 100*mean(ep < cfg.max_epochs), mean(acc), ...
           'VariableNames', {'Entradas', 'Activacion', 'Momento', 'Epocas', 'Convergio', 'Exactitud'})];
end
cfg = cfg_base;
R3b

figure; colororder(paleta); hold on
for n_in = [2 3]
    [X, D] = xor_data(n_in);
    cfg = cfg_base;  cfg.n_inputs = n_in;  cfg.hidden_layers = [4];  cfg.momentum = 0.9;
    [~, hist] = train_mlp(X, D, [], [], cfg);
    plot(hist.train, 'LineWidth', 1.3, 'DisplayName', sprintf('MLP, XOR de %d entradas, \\beta = 0.9', n_in))
end
cfgA.n_inputs = 2;  rng(1);  [~, ~, mse_hist] = train_adaline(xor_data(2), [0; 1; 1; 0], cfgA);
plot(mse_hist, 'LineWidth', 1.3, 'DisplayName', 'Adaline, XOR de 2 entradas')
set(gca, 'YScale', 'log'); grid on; legend; xlabel('época'); ylabel('error cuadrático medio')
cfg = cfg_base;
%% 10. Numeral 4, clasificación multiclase con Iris
% Tres salidas con codificación uno contra el resto y decisión por la mayor
% salida. Partición 70-30, y dentro del 70 se reserva una quinta parte como
% validación para la curva de error, de modo que la prueba no interviene en
% el entrenamiento. Se prueban tres arquitecturas de una capa, una de dos capas
% y tres tasas de aprendizaje.

[X_iris, D_iris] = load_dataset('iris', cfg);
[Xtr, Dtr, Xva, Dva, Xte, Dte] = split_train_val_test(X_iris, D_iris, 0.7, cfg);
Ttr = onehot(Dtr, 3);  Tva = onehot(Dva, 3);
ocultas_iris = {[3], [6], [12], [8 4]};
etas_iris = [0.05 0.1 0.3];
cfg = cfg_base;  cfg.n_inputs = 4;  cfg.n_outputs = 3;  cfg.max_epochs = 1000;
n_arq = numel(ocultas_iris);
R4 = table();  curvas = cell(n_arq, 3);  confusiones = cell(n_arq, 3);
for h = 1:n_arq
    for e = 1:3
        cfg.hidden_layers = ocultas_iris{h};  cfg.eta = etas_iris(e);
        tic;  [net, hist] = train_mlp(Xtr, Ttr, Xva, Tva, cfg);  t = toc;
        pred = predict_mlp(net, Xte, cfg);
        confusiones{h, e} = confusionmat(Dte, pred);
        curvas{h, e} = hist;
        R4 = [R4; table({mat2str(ocultas_iris{h})}, etas_iris(e), hist.epochs, t, hist.train(end), hist.val(end), 100*mean(pred == Dte), ...
              'VariableNames', {'Ocultas', 'Eta', 'Epocas', 'Segundos', 'MSE_entrenamiento', 'MSE_validacion', 'Exactitud'})];
    end
end
R4

figure; colororder(paleta)
for h = 1:n_arq
    for e = 1:3
        subplot(n_arq, 3, (h-1)*3 + e); hold on
        plot(curvas{h, e}.train, 'LineWidth', 1.1); plot(curvas{h, e}.val, 'LineWidth', 1.1)
        title(sprintf('ocultas %s, \\eta = %g', mat2str(ocultas_iris{h}), etas_iris(e)), 'FontSize', 8)
        grid on; xlim([1 cfg.max_epochs]); ylim([0 0.4])
        if h == n_arq, xlabel('época'); end
        if e == 1, ylabel('MSE'); end
        if h == 1 && e == 1, legend('entrenamiento', 'validación', 'Location', 'northeast'); end
    end
end

[~, mejor] = max(R4.Exactitud);
hm = ceil(mejor / 3);  em = mod(mejor - 1, 3) + 1;
Confusion_mejor = array2table(confusiones{hm, em}, 'RowNames', {'setosa', 'versicolor', 'virginica'}, ...
    'VariableNames', {'pred_setosa', 'pred_versicolor', 'pred_virginica'})

R4_confusiones = table();
for h = 1:n_arq
    for e = 1:3
        C = confusiones{h, e};
        R4_confusiones = [R4_confusiones; table({mat2str(ocultas_iris{h})}, etas_iris(e), C(1,1), C(1,2), C(1,3), C(2,1), C(2,2), C(2,3), C(3,1), C(3,2), C(3,3), ...
            'VariableNames', {'Ocultas', 'Eta', 'se_se', 'se_ve', 'se_vi', 've_se', 've_ve', 've_vi', 'vi_se', 'vi_ve', 'vi_vi'})];
    end
end
R4_confusiones
%% 11. Numeral 5, Wine, Breast Cancer Wisconsin y billetes por particiones
% Se generan las particiones 60-40, 70-30, 80-20 y 90-10 con la misma función
% del Taller 1 y se entrena el MLP, el Perceptrón y el Adaline sobre cada una.
% La parada temprana del MLP vigila una quinta parte del entrenamiento y la
% exactitud se mide sobre la prueba, que no interviene. Wine tiene tres clases,
% así que el Perceptrón y el Adaline se entrenan con una neurona por clase y
% deciden por la mayor suma ponderada.

proporciones = [0.6 0.7 0.8 0.9];
conjuntos = {'wine', 'wdbc', 'banknote'};
nombres_conjuntos = {'Wine', 'Breast Cancer', 'Billetes'};
R5 = table();
for c = 1:numel(conjuntos)
    [Xd, Dd] = load_dataset(conjuntos{c}, cfg_base);
    n_clases = numel(unique(Dd));
    for r = proporciones
        [Xtr, Dtr, Xva, Dva, Xte, Dte] = split_train_val_test(Xd, Dd, r, cfg_base);
        cfg = cfg_base;  cfg.n_inputs = size(Xtr, 2);  cfg.max_epochs = 500;  cfg.patience = 30;
        if n_clases > 2
            cfg.n_outputs = n_clases;  Ttr = onehot(Dtr, n_clases);  Tva = onehot(Dva, n_clases);
        else
            cfg.n_outputs = 1;  Ttr = Dtr;  Tva = Dva;
        end
        cfg.hidden_layers = [8];
        tic;  [net, hist] = train_mlp(Xtr, Ttr, Xva, Tva, cfg);  t_mlp = toc;
        acc_mlp = 100*mean(predict_mlp(net, Xte, cfg) == Dte);

        Xtr_lineal = [Xtr; Xva];  Dtr_lineal = [Dtr; Dva];
        cfgP.n_inputs = size(Xtr, 2);  cfgA.n_inputs = size(Xtr, 2);
        tic;  [acc_p, ep_p] = one_vs_rest(Xtr_lineal, Dtr_lineal, Xte, Dte, cfgP, 'perceptron');  t_p = toc;
        tic;  [acc_a, ep_a] = one_vs_rest(Xtr_lineal, Dtr_lineal, Xte, Dte, cfgA, 'adaline');     t_a = toc;

        R5 = [R5; table(conjuntos(c), r, acc_mlp, hist.epochs, t_mlp, acc_p, ep_p, t_p, acc_a, ep_a, t_a, ...
              'VariableNames', {'Conjunto', 'Proporcion', 'MLP', 'Epocas_MLP', 'Seg_MLP', 'Perceptron', 'Epocas_P', 'Seg_P', 'Adaline', 'Epocas_A', 'Seg_A'})];
    end
end
cfg = cfg_base;
R5

figure; colororder(paleta)
for c = 1:3
    subplot(1, 3, c); hold on
    m = strcmp(R5.Conjunto, conjuntos{c});
    plot(proporciones, R5.MLP(m), '-o', 'LineWidth', 1.3)
    plot(proporciones, R5.Perceptron(m), '-s', 'LineWidth', 1.3)
    plot(proporciones, R5.Adaline(m), '-^', 'LineWidth', 1.3)
    xticks(proporciones); xticklabels({'60-40', '70-30', '80-20', '90-10'})
    title(nombres_conjuntos{c}); grid on; xlabel('partición')
    if c == 1, ylabel('exactitud de prueba (%)'); end
end
legend('MLP', 'Perceptrón', 'Adaline', 'Location', 'southeast')
%% 12. Numeral 6, sobreajuste y parada temprana
% Sobre Breast Cancer Wisconsin con la partición 70-30, y una quinta parte del
% entrenamiento reservada como validación, se entrena con distinto número de
% neuronas ocultas durante muchas épocas y sin parada temprana, para ver el
% error de entrenamiento y el de validación en la misma figura. Después se
% repite con parada temprana por épocas sin mejora en validación, y la
% exactitud se mide siempre sobre la prueba.

[Xd, Dd] = load_dataset('wdbc', cfg_base);
[Xtr, Dtr, Xva, Dva, Xte, Dte] = split_train_val_test(Xd, Dd, 0.7, cfg_base);
ocultas_sobre = {[2], [8], [32], [64]};
cfg = cfg_base;  cfg.n_inputs = size(Xtr, 2);  cfg.n_outputs = 1;  cfg.max_epochs = 1500;  cfg.eta = 0.1;  cfg.target_error = 0;
R6 = table();  curvas_sobre = cell(1, 4);
for h = 1:4
    cfg.hidden_layers = ocultas_sobre{h};
    cfg.patience = 0;
    [net, hist] = train_mlp(Xtr, Dtr, Xva, Dva, cfg);
    curvas_sobre{h} = hist;
    [~, ep_min] = min(hist.val);
    acc_final = 100*mean(predict_mlp(net, Xte, cfg) == Dte);
    cfg.patience = 50;
    [net_es, hist_es] = train_mlp(Xtr, Dtr, Xva, Dva, cfg);
    acc_es = 100*mean(predict_mlp(net_es, Xte, cfg) == Dte);
    R6 = [R6; table({mat2str(ocultas_sobre{h})}, hist.train(end), hist.val(end), ep_min, min(hist.val), acc_final, hist_es.epochs, acc_es, ...
          'VariableNames', {'Ocultas', 'MSE_entren_final', 'MSE_val_final', 'Epoca_val_minimo', 'MSE_val_minimo', 'Exact_sin_parada', 'Epocas_con_parada', 'Exact_con_parada'})];
end
R6

epocas_sobre = [200 500 1000 1500];
cfg.hidden_layers = [8];  cfg.patience = 0;
R6b = table();
for ne = epocas_sobre
    cfg.max_epochs = ne;
    [net, hist] = train_mlp(Xtr, Dtr, Xva, Dva, cfg);
    R6b = [R6b; table(ne, hist.train(end), hist.val(end), 100*mean(predict_mlp(net, Xte, cfg) == Dte), ...
           'VariableNames', {'Epocas', 'MSE_entrenamiento', 'MSE_validacion', 'Exactitud_prueba'})];
end
cfg = cfg_base;
R6b

figure; colororder(paleta)
for h = 1:4
    subplot(2, 2, h); hold on
    plot(curvas_sobre{h}.train, 'LineWidth', 1.2); plot(curvas_sobre{h}.val, 'LineWidth', 1.2)
    xline(R6.Epoca_val_minimo(h), '--', 'Color', paleta(6, :))
    title(sprintf('%s neuronas ocultas', mat2str(ocultas_sobre{h}))); grid on
    xlabel('época'); ylabel('MSE'); set(gca, 'YScale', 'log'); ylim([1e-3 1e-1])
    if h == 1, legend('entrenamiento', 'validación', 'mínimo de validación', 'Location', 'northeast'); end
end
%% Funciones locales
% MATLAB permite definir funciones locales al final de un script. No cambie
% los nombres ni los argumentos de entrada/salida.

function net = init_mlp(cfg)
    % Inicializa pesos y sesgos de todas las capas en la estructura `net`.
    net = struct();
    net.W = {};
    net.b = {};
    net.dW_prev = {};
    net.db_prev = {};
    layer_sizes = [cfg.n_inputs, cfg.hidden_layers, cfg.n_outputs];
    for k = 1:numel(layer_sizes) - 1
        net.W{k} = randn(layer_sizes(k+1), layer_sizes(k)) * cfg.init_scale;
        net.b{k} = zeros(layer_sizes(k+1), 1);
        net.dW_prev{k} = zeros(size(net.W{k}));
        net.db_prev{k} = zeros(size(net.b{k}));
    end
end

function [y, cache] = forward_mlp(net, x, cfg)
    % Propaga la entrada x a través de todas las capas de la red.
    a{1} = x;
    L = numel(net.W);
    for k = 1:L
        netv{k} = net.W{k} * a{k} + net.b{k};
        if k == L
            a{k+1} = activation(netv{k}, cfg.act_output);
        else
            a{k+1} = activation(netv{k}, hidden_act(cfg, k));
        end
    end
    y = a{end};
    cache.a = a;
    cache.netv = netv;
end

function tipo = hidden_act(cfg, k)
    % Activación de la capa oculta k, una para todas o una por capa si act_hidden es celda.
    if iscell(cfg.act_hidden), tipo = cfg.act_hidden{k}; else, tipo = cfg.act_hidden; end
end

function net = backward_mlp(net, cache, x, d, cfg)
    % Calcula los delta de cada capa y actualiza los pesos (ver fórmulas
    % de la Sección 1 de este mismo script).
    L = numel(net.W);
    delta = cell(1, L);
    delta{L} = (d - cache.a{L+1}) .* activation_deriv(cache.netv{L}, cfg.act_output);
    for k = L-1:-1:1
        delta{k} = (net.W{k+1}' * delta{k+1}) .* activation_deriv(cache.netv{k}, hidden_act(cfg, k));
    end
    for k = 1:L
        dW = cfg.eta * delta{k} * cache.a{k}' + cfg.momentum * net.dW_prev{k};
        db = cfg.eta * delta{k} + cfg.momentum * net.db_prev{k};
        net.W{k} = net.W{k} + dW;
        net.b{k} = net.b{k} + db;
        net.dW_prev{k} = dW;
        net.db_prev{k} = db;
    end
end

function y = activation(net_in, tipo)
    switch tipo
        case 'sigmoid'
            y = 1 ./ (1 + exp(-net_in));
        case 'tanh'
            y = tanh(net_in);
        case 'relu'
            y = max(0, net_in);
        case 'linear'
            y = net_in;
        otherwise
            error('Función de activación no reconocida: %s', tipo);
    end
end

function dy = activation_deriv(net_in, tipo)
    % Derivada de la función de activación, evaluada en net_in.
    switch tipo
        case 'sigmoid'
            f = 1 ./ (1 + exp(-net_in));
            dy = f .* (1 - f);
        case 'tanh'
            dy = 1 - tanh(net_in).^2;
        case 'relu'
            dy = double(net_in > 0);
        case 'linear'
            dy = ones(size(net_in));
        otherwise
            error('Función de activación no reconocida: %s', tipo);
    end
end

function [net, hist] = train_mlp(Xtr, Dtr, Xva, Dva, cfg)
    % Mismo ciclo de la sección 8, con error de validación por época y parada
    % temprana cuando la validación lleva cfg.patience épocas sin mejorar.
    rng(cfg.seed);
    net = init_mlp(cfg);
    hist.train = zeros(cfg.max_epochs, 1);  hist.val = hist.train;
    mejor = Inf;  sin_mejora = 0;  mejor_net = net;
    for epoch = 1:cfg.max_epochs
        for p = randperm(size(Xtr, 1))
            [~, cache] = forward_mlp(net, Xtr(p, :)', cfg);
            net = backward_mlp(net, cache, Xtr(p, :)', Dtr(p, :)', cfg);
        end
        hist.train(epoch) = mse_mlp(net, Xtr, Dtr, cfg);
        if ~isempty(Xva), hist.val(epoch) = mse_mlp(net, Xva, Dva, cfg); end
        if hist.train(epoch) <= cfg.target_error, break; end
        if cfg.patience > 0 && ~isempty(Xva)
            if hist.val(epoch) < mejor
                mejor = hist.val(epoch);  sin_mejora = 0;  mejor_net = net;
            else
                sin_mejora = sin_mejora + 1;
                if sin_mejora >= cfg.patience, net = mejor_net; break; end
            end
        end
    end
    hist.train = hist.train(1:epoch);  hist.val = hist.val(1:epoch);  hist.epochs = epoch;
end

function e = mse_mlp(net, X, D, cfg)
    % Error cuadrático medio de la red sobre un conjunto, patrones por filas.
    Y = forward_mlp(net, X', cfg);
    e = mean(0.5 * sum((D' - Y).^2, 1));
end

function clase = predict_mlp(net, X, cfg)
    % Clase predicha, por umbral 0.5 con una salida o por la mayor salida con varias.
    Y = forward_mlp(net, X', cfg);
    if cfg.n_outputs == 1
        clase = double(Y' >= cfg.threshold);
    else
        [~, clase] = max(Y, [], 1);  clase = clase';
    end
end

function acc = accuracy_mlp(net, X, D, cfg)
    acc = 100 * mean(predict_mlp(net, X, cfg) == D);
end

function [X, D] = xor_data(n_inputs)
    % Tabla de verdad de la XOR de n entradas, salida 1 con un número impar de unos.
    X = zeros(2^n_inputs, n_inputs);
    for p = 0:2^n_inputs - 1
        X(p+1, :) = bitget(p, n_inputs:-1:1);
    end
    D = mod(sum(X, 2), 2);
end

function T = onehot(D, n_clases)
    T = double(D == 1:n_clases);
end

function [X, D] = load_dataset(nombre, cfg)
    % Carga cada conjunto con la clase como entero desde 1, o 0 y 1 si es binaria.
    switch nombre
        case 'iris'
            M = load(cfg.datos.iris);  X = M(:, 1:4);  D = M(:, 5);
        case 'wine'
            M = readmatrix(cfg.datos.wine, 'FileType', 'text');  X = M(:, 2:end);  D = M(:, 1);
        case 'wdbc'
            T = readtable(cfg.datos.wdbc, 'FileType', 'text', 'ReadVariableNames', false);
            X = T{:, 3:end};  D = double(strcmp(T{:, 2}, 'M'));
        case 'banknote'
            M = readmatrix(cfg.datos.banknote);  X = M(:, 1:4);  D = M(:, 5);
    end
end

function [Xtr, Dtr, Xte, Dte] = split_dataset(X, D, train_ratio, seed)
    % Misma partición del Taller 1, mezcla con semilla y corte por proporción.
    rng(seed);
    n = size(X, 1);
    idx = randperm(n);
    n_train = round(train_ratio * n);
    Xtr = X(idx(1:n_train), :);      Dtr = D(idx(1:n_train), :);
    Xte = X(idx(n_train+1:end), :);  Dte = D(idx(n_train+1:end), :);
end

function [Xtr, Dtr, Xva, Dva, Xte, Dte] = split_train_val_test(X, D, train_ratio, cfg)
    % Parte en entrenamiento y prueba con la proporción pedida, aparta de la parte
    % de entrenamiento la fracción de validación y escala todo con el entrenamiento.
    [Xtr, Dtr, Xte, Dte] = split_dataset(X, D, train_ratio, cfg.seed);
    [Xtr, Dtr, Xva, Dva] = split_dataset(Xtr, Dtr, 1 - cfg.val_fraction, cfg.seed + 1);
    mn = min(Xtr);  mx = max(Xtr);  mx(mx == mn) = mn(mx == mn) + 1;
    Xtr = (Xtr - mn) ./ (mx - mn);  Xva = (Xva - mn) ./ (mx - mn);  Xte = (Xte - mn) ./ (mx - mn);
end

function [Xtr, Xte] = scale_minmax(Xtr, Xte)
    % Escala cada columna al rango 0 a 1 con los mínimos y máximos del entrenamiento.
    mn = min(Xtr);  mx = max(Xtr);  mx(mx == mn) = mn(mx == mn) + 1;
    Xtr = (Xtr - mn) ./ (mx - mn);
    Xte = (Xte - mn) ./ (mx - mn);
end

function [W, b, epochs_to_converge] = train_perceptron(X, D, cfg)
    % Perceptrón del Taller 1, regla 3, sin cambios.
    W = randn(1, cfg.n_inputs) * cfg.init_scale;  b = randn(1) * cfg.init_scale;
    epochs_to_converge = cfg.max_epochs;
    for epoch = 1:cfg.max_epochs
        n_errors = 0;
        for p = 1:size(X, 1)
            y = double(W * X(p, :)' + b >= cfg.threshold);
            if y ~= D(p), n_errors = n_errors + 1; end
            W = W + cfg.alpha * (D(p) - y) * X(p, :);
            b = b + (D(p) - y);
        end
        if n_errors == 0, epochs_to_converge = epoch; break; end
    end
end

function [W, b, mse_hist] = train_adaline(X, D, cfg)
    % Adaline del Taller 1, Regla Delta sobre la salida lineal, sin cambios.
    W = randn(1, cfg.n_inputs) * cfg.init_scale;  b = randn(1) * cfg.init_scale;
    mse_hist = zeros(cfg.max_epochs, 1);
    for epoch = 1:cfg.max_epochs
        epoch_error = 0;
        for p = 1:size(X, 1)
            y = W * X(p, :)' + b;
            W = W + cfg.alpha * (D(p) - y) * X(p, :);
            b = b + cfg.alpha * (D(p) - y);
            epoch_error = epoch_error + 0.5 * (D(p) - y)^2;
        end
        mse_hist(epoch) = epoch_error / size(X, 1);
        if mse_hist(epoch) <= cfg.target_mse, mse_hist = mse_hist(1:epoch); break; end
    end
end

function acc = accuracy_of(X, D, W, b, threshold)
    acc = 100 * mean(double(X * W' + b >= threshold) == D);
end

function [acc, epocas] = one_vs_rest(Xtr, Dtr, Xte, Dte, cfg, modelo)
    % Una neurona por clase cuando hay más de dos, decisión por la mayor suma ponderada.
    clases = unique(Dtr);
    if numel(clases) == 2
        rng(cfg.seed);
        if strcmp(modelo, 'perceptron')
            [W, b, epocas] = train_perceptron(Xtr, Dtr, cfg);
        else
            [W, b, mse_hist] = train_adaline(Xtr, Dtr, cfg);  epocas = numel(mse_hist);
        end
        acc = accuracy_of(Xte, Dte, W, b, cfg.threshold);
        return
    end
    Z = zeros(size(Xte, 1), numel(clases));  epocas = 0;
    for c = 1:numel(clases)
        rng(cfg.seed);
        if strcmp(modelo, 'perceptron')
            [W, b, ep] = train_perceptron(Xtr, double(Dtr == clases(c)), cfg);
        else
            [W, b, mse_hist] = train_adaline(Xtr, double(Dtr == clases(c)), cfg);  ep = numel(mse_hist);
        end
        Z(:, c) = Xte * W' + b;  epocas = max(epocas, ep);
    end
    [~, pred] = max(Z, [], 2);
    acc = 100 * mean(clases(pred) == Dte);
end
