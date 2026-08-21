function T = evaluar_cv(X, y, opciones)
% Validacion cruzada estratificada a mano (k particiones).
%
% La gracia de hacerla a mano y no con crossval() es que el balanceo y el
% escalado se aplican SOLO al bloque de entrenamiento de cada iteracion.
% Si se aplican antes de partir, el bloque de prueba queda contaminado y
% las metricas salen infladas (eso es justo lo que compara el informe).
%
%   opciones.k         -> numero de particiones (5 por defecto)
%   opciones.semilla   -> para poder repetir el experimento
%   opciones.balanceo  -> 'ninguno' | 'smote' | 'submuestreo' | 'sobremuestreo'
%   opciones.escala    -> 'ninguna' | 'zscore' | 'minmax'
%   opciones.modelos   -> {'Arbol','KNN','LDA','NaiveBayes','SVM','Logistica'}
%   opciones.clase_pos -> nombre de la clase positiva (si es binario)

if ~isfield(opciones,'k'),         opciones.k = 5; end
if ~isfield(opciones,'semilla'),   opciones.semilla = 42; end
if ~isfield(opciones,'balanceo'),  opciones.balanceo = 'ninguno'; end
if ~isfield(opciones,'escala'),    opciones.escala = 'ninguna'; end
if ~isfield(opciones,'modelos'),   opciones.modelos = {'Arbol','KNN','LDA'}; end
if ~isfield(opciones,'clase_pos'), opciones.clase_pos = ''; end

y = cellstr(y);
clases = unique(y);
rng(opciones.semilla);

% en el dataset crudo hay clases con 2 muestras, asi que algun fold se queda
% sin ellas. MATLAB avisa; lo silenciamos porque justamente eso es lo que
% queremos mostrar (el crudo no se puede validar bien) y si no llena la consola.
warning('off','stats:cvpartition:KFoldMissingGrp');
part = cvpartition(y, 'KFold', opciones.k);

nm = numel(opciones.modelos);
res = nan(nm, 7);
tiempos = zeros(nm, 1);

for im = 1:nm
    nombre = opciones.modelos{im};
    yreal_todo = {}; ypred_todo = {};
    t0 = tic;
    ok = true;
    for f = 1:opciones.k
        itr = training(part, f);  ite = test(part, f);
        Xtr = X(itr, :); ytr = y(itr);
        Xte = X(ite, :); yte = y(ite);

        % --- balanceo solo con los datos de entrenamiento
        if ~strcmp(opciones.balanceo, 'ninguno')
            [Xtr, ytr] = balancear(Xtr, ytr, opciones.balanceo);
        end

        % --- escalado: los parametros salen del entrenamiento y se
        %     aplican tal cual al bloque de prueba
        switch opciones.escala
            case 'zscore'
                mu = mean(Xtr); sg = std(Xtr); sg(sg == 0) = 1;
                Xtr = (Xtr - mu) ./ sg;  Xte = (Xte - mu) ./ sg;
            case 'minmax'
                mn = min(Xtr); mx = max(Xtr); rg = mx - mn; rg(rg == 0) = 1;
                Xtr = (Xtr - mn) ./ rg;  Xte = (Xte - mn) ./ rg;
        end

        try
            mdl = entrenar(nombre, Xtr, ytr);
            yp  = predict(mdl, Xte);
        catch ME
            fprintf('  [!] %s fallo: %s\n', nombre, ME.message);
            ok = false; break
        end
        yreal_todo = [yreal_todo; yte];          %#ok<AGROW>
        ypred_todo = [ypred_todo; cellstr(yp)];  %#ok<AGROW>
    end
    tiempos(im) = toc(t0);

    if ok
        m = metricas_clf(yreal_todo, ypred_todo, clases, opciones.clase_pos);
        res(im, :) = [m.exactitud, m.exact_balance, m.f1_macro, m.kappa, ...
                      m.recall_pos, m.precision_pos, m.f1_pos];
    end
end

T = table(opciones.modelos(:), res(:,1), res(:,2), res(:,3), res(:,4), ...
          res(:,5), res(:,6), res(:,7), tiempos, ...
    'VariableNames', {'Modelo','Exactitud','ExactBalanceada','F1_macro', ...
                      'Kappa','Recall_pos','Precision_pos','F1_pos','Segundos'});
end


function mdl = entrenar(nombre, X, y)
switch nombre
    case 'Arbol'
        mdl = fitctree(X, y);
    case 'KNN'
        mdl = fitcknn(X, y, 'NumNeighbors', 5, 'Distance', 'euclidean');
    case 'LDA'
        % pseudoLinear evita que reviente si hay columnas colineales
        mdl = fitcdiscr(X, y, 'DiscrimType', 'pseudoLinear');
    case 'NaiveBayes'
        mdl = fitcnb(X, y, 'DistributionNames', 'kernel');
    case 'SVM'
        t = templateSVM('KernelFunction', 'linear', 'Standardize', true);
        mdl = fitcecoc(X, y, 'Learners', t);
    case 'Logistica'
        mdl = fitclinear(X, y, 'Learner', 'logistic');
    otherwise
        error('Modelo no reconocido: %s', nombre);
end
end
