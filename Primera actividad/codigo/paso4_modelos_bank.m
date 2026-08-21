%% =======================================================================
%  BANK MARKETING - Modelos en cada etapa del dataset
%
%  Que modelos se usan y por que:
%   Arbol      - aguanta variables mezcladas y no le afecta la escala.
%   KNN        - justo lo contrario, es el que mas deberia notar el escalado.
%   LDA        - ruta parametrica clasica.
%   Logistica  - el modelo de referencia para un problema binario como este.
%   SVM lineal - solo en las etapas balanceadas. Con 45211 filas el
%                entrenamiento se dispara y no aporta nada nuevo al analisis.
%
%  Naive Bayes se deja por fuera a proposito: asume que las predictoras son
%  independientes dentro de cada clase, y las columnas one-hot de una misma
%  variable son excluyentes entre si, o sea lo mas dependiente que hay.
% =======================================================================
clear; clc; close all;
rng(42);

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'bank', 'figuras');
xls     = fullfile(base, 'Resultados_Bank.xlsx');
load(fullfile(base, 'resultados', 'bank', 'bank_etapas.mat'));
load(fullfile(base, 'resultados', 'bank', 'bank_crudo.mat'), 'y', 'clase_pos');

tope_svm = 15000;

%% --- (a) Validacion directa sobre cada etapa ---------------------------
Res = table();
for i = 1:numel(E)
    if size(E(i).X,1) > tope_svm
        mods = {'Arbol','KNN','LDA','Logistica'};
        fprintf('--- %s (n=%d, se omite SVM por costo) ---\n', E(i).nombre, size(E(i).X,1));
    else
        mods = {'Arbol','KNN','LDA','Logistica','SVM'};
        fprintf('--- %s (n=%d) ---\n', E(i).nombre, size(E(i).X,1));
    end
    op = struct('k',5, 'semilla',42, 'modelos',{mods}, 'clase_pos',clase_pos);
    Ti = evaluar_cv(E(i).X, E(i).y, op);
    Ti.Etapa = repmat({E(i).nombre}, height(Ti), 1);
    Ti.N     = repmat(size(E(i).X,1), height(Ti), 1);
    % Referencia de cada etapa: acertar siempre la clase mayoritaria. Ojo que
    % NO es la misma en todas: en B0/B1 vale 0.883 y en las balanceadas 0.5,
    % asi que las exactitudes de una etapa y otra no se comparan de frente.
    % Para eso esta la columna de mejora sobre la base.
    base_i = max(mean(strcmp(E(i).y,'no')), mean(strcmp(E(i).y,'yes')));
    Ti.Tasa_base_etapa   = repmat(base_i, height(Ti), 1);
    Ti.Mejora_sobre_base = Ti.Exactitud - base_i;
    Res = [Res; Ti];   %#ok<AGROW>
end
Res = movevars(Res, {'Etapa','N'}, 'Before', 'Modelo');
tasa_base = mean(strcmp(y,'no'));
disp(Res);
fprintf('\nTasa base del dataset original (predecir siempre "no"): %.4f\n', tasa_base);

%% --- (b) Validacion honesta -------------------------------------------
% Se parte de B1 sin balancear y el submuestreo se hace dentro de cada fold,
% de modo que el bloque de prueba conserva la proporcion real 88/12.
mods = {'Arbol','KNN','LDA','Logistica'};
configs = { 'H0_sin_nada',       'ninguno',     'ninguna'; ...
            'H1_sub_en_fold',    'submuestreo', 'ninguna'; ...
            'H2_sub_zscore',     'submuestreo', 'zscore' ; ...
            'H3_sub_minmax',     'submuestreo', 'minmax' };

Honesta = table();
for c = 1:size(configs,1)
    fprintf('--- %s ---\n', configs{c,1});
    op = struct('k',5, 'semilla',42, 'modelos',{mods}, ...
                'balanceo',configs{c,2}, 'escala',configs{c,3}, 'clase_pos',clase_pos);
    Tc = evaluar_cv(E(2).X, E(2).y, op);
    Tc.Config = repmat(configs(c,1), height(Tc), 1);
    Honesta = [Honesta; Tc];   %#ok<AGROW>
end
Honesta = movevars(Honesta, 'Config', 'Before', 'Modelo');
disp(Honesta);

%% --- Comparacion directa vs honesta -----------------------------------
pares = {'B2_balanceado','H1_sub_en_fold'; ...
         'B3_estandarizado','H2_sub_zscore'; ...
         'B4_normalizado','H3_sub_minmax'};
filas = {};
for p = 1:size(pares,1)
    for m = 1:numel(mods)
        a = Res.ExactBalanceada(strcmp(Res.Etapa,pares{p,1}) & strcmp(Res.Modelo,mods{m}));
        b = Honesta.ExactBalanceada(strcmp(Honesta.Config,pares{p,2}) & strcmp(Honesta.Modelo,mods{m}));
        filas(end+1,:) = {pares{p,1}, pares{p,2}, mods{m}, a, b, a-b};   %#ok<SAGROW>
    end
end
Fuga = cell2table(filas, 'VariableNames', ...
    {'Etapa_directa','Config_honesta','Modelo','ExactBal_directa','ExactBal_honesta','Diferencia'});
disp('--- Directa vs honesta ---'); disp(Fuga);
fprintf('Diferencia promedio: %.4f\n', mean(Fuga.Diferencia));

%% --- Graficos ---------------------------------------------------------
nombres = {E.nombre};
mods_todos = {'Arbol','KNN','LDA','Logistica'};
M  = nan(numel(nombres), numel(mods_todos));
M2 = nan(numel(nombres), numel(mods_todos));
for i = 1:numel(nombres)
    for m = 1:numel(mods_todos)
        k = strcmp(Res.Etapa,nombres{i}) & strcmp(Res.Modelo,mods_todos{m});
        if any(k)
            M(i,m)  = Res.ExactBalanceada(k);
            M2(i,m) = Res.Exactitud(k);
        end
    end
end

f = figure('Visible','off','Position',[100 100 1150 520]);
subplot(2,1,1);
bar(M2); ylim([0 1]); grid on; ylabel('exactitud');
hold on; yline(tasa_base, 'r--', 'siempre "no"');
set(gca,'XTickLabel', strrep(nombres,'_',' '), 'XTickLabelRotation', 15, 'FontSize', 8);
title('Exactitud simple: en las etapas sin balancear apenas le gana a "siempre no"');
subplot(2,1,2);
bar(M); ylim([0 1]); grid on; ylabel('exactitud balanceada');
hold on; yline(0.5, 'r--', 'azar');
set(gca,'XTickLabel', strrep(nombres,'_',' '), 'XTickLabelRotation', 15, 'FontSize', 8);
legend(mods_todos, 'Location','southoutside','Orientation','horizontal');
title('Exactitud balanceada: aqui si se ve lo que aporta cada correccion');
sgtitle('Bank - desempeno por etapa (validacion directa, CV 5-fold)');
guardar_fig(f, dir_fig, '12_modelos_por_etapa');

% recall de la clase minoritaria, que es lo que de verdad le interesa al banco
f = figure('Visible','off','Position',[100 100 1000 450]);
Rc = nan(numel(nombres), numel(mods_todos));
for i = 1:numel(nombres)
    for m = 1:numel(mods_todos)
        k = strcmp(Res.Etapa,nombres{i}) & strcmp(Res.Modelo,mods_todos{m});
        if any(k), Rc(i,m) = Res.Recall_pos(k); end
    end
end
bar(Rc); ylim([0 1]); grid on;
set(gca,'XTickLabel', strrep(nombres,'_',' '), 'XTickLabelRotation', 15, 'FontSize', 8);
ylabel('recall de la clase "yes"');
legend(mods_todos, 'Location','southoutside','Orientation','horizontal');
title('Bank - cuantos clientes que si contratan logra detectar el modelo');
guardar_fig(f, dir_fig, '13_recall_clase_minoritaria');

% directa vs honesta
f = figure('Visible','off','Position',[100 100 950 450]);
Md = reshape(Fuga.ExactBal_directa, numel(mods), []);
Mh = reshape(Fuga.ExactBal_honesta, numel(mods), []);
bar([Md(:,1) Mh(:,1)]); ylim([0 1]); grid on;
set(gca,'XTickLabel',mods,'XTickLabelRotation',15);
legend({'submuestreo antes de partir','submuestreo dentro del fold'},'Location','southoutside');
ylabel('exactitud balanceada');
title('Bank - efecto de balancear antes de separar entrenamiento y prueba');
guardar_fig(f, dir_fig, '14_fuga_por_balanceo');

% Matriz de confusion del mejor modelo por exactitud balanceada, pero SIN
% contar B0: esa etapa gana solo porque todavia tiene duration, o sea con
% informacion que en la vida real no se tiene antes de hacer la llamada.
candidatas = ~strcmp(Res.Etapa, 'B0_crudo');
eb = Res.ExactBalanceada;  eb(~candidatas) = -Inf;
[~, imej] = max(eb);
etapa_mej = Res.Etapa{imej};  mod_mej = Res.Modelo{imej};
ie = find(strcmp({E.nombre}, etapa_mej));
part = cvpartition(E(ie).y, 'KFold', 5);
yreal = {}; ypred = {};
for fo = 1:5
    itr = training(part,fo); ite = test(part,fo);
    switch mod_mej
        case 'Arbol',     mdl = fitctree(E(ie).X(itr,:), E(ie).y(itr));
        case 'KNN',       mdl = fitcknn(E(ie).X(itr,:), E(ie).y(itr), 'NumNeighbors',5);
        case 'LDA',       mdl = fitcdiscr(E(ie).X(itr,:), E(ie).y(itr), 'DiscrimType','pseudoLinear');
        case 'Logistica', mdl = fitclinear(E(ie).X(itr,:), E(ie).y(itr), 'Learner','logistic');
        case 'SVM',       mdl = fitcecoc(E(ie).X(itr,:), E(ie).y(itr), ...
                                'Learners', templateSVM('KernelFunction','linear','Standardize',true));
    end
    yreal = [yreal; E(ie).y(ite)];                            %#ok<AGROW>
    ypred = [ypred; cellstr(predict(mdl, E(ie).X(ite,:)))];   %#ok<AGROW>
end
f = figure('Visible','off','Position',[100 100 600 520]);
confusionchart(yreal, ypred, 'RowSummary','row-normalized');
title(sprintf('Bank - %s sobre %s', mod_mej, strrep(etapa_mej,'_',' ')));
guardar_fig(f, dir_fig, '15_confusion_mejor');

%% --- Exportar ---------------------------------------------------------
writetable(Res,     xls, 'Sheet', 'B4_Modelos_directa');
writetable(Honesta, xls, 'Sheet', 'B4_Modelos_honesta');
writetable(Fuga,    xls, 'Sheet', 'B4_Comparacion_fuga');
save(fullfile(base,'resultados','bank','bank_modelos.mat'), 'Res','Honesta','Fuga','tasa_base');
fprintf('\nPaso 4 (modelos bank) terminado. Mejor: %s sobre %s (exact. balanceada %.3f)\n', ...
        mod_mej, etapa_mej, Res.ExactBalanceada(imej));
