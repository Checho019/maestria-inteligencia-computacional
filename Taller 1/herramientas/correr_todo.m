function correr_todo
% Corre los once scripts del taller en orden y genera los .mlx ejecutados
% con su PDF. Se llama desde la carpeta del taller.
scripts = {'T0_Dataset_train_test','T1_perceptron_compuertas','T2_perceptron_iris', ...
           'T3_dataset_banknote','T4_perceptron_banknote','T5_adaline_compuertas', ...
           'T6_adaline_iris','T7_adaline_banknote', ...
           'R1_revision_iris','R2_revision_banknote','R3_modelos_por_paso'};
for k = 1:numel(scripts)
    fprintf('\n######## %s ########\n', scripts{k});
    try
        correr(scripts{k});
        fprintf('>>> OK %s\n', scripts{k});
    catch e
        fprintf('>>> ERROR en %s: %s\n', scripts{k}, e.message);
        for j = 1:numel(e.stack), fprintf('    %s linea %d\n', e.stack(j).name, e.stack(j).line); end
    end
    close all
end
if ~exist('mlx','dir'), mkdir('mlx'); end
if ~exist('pdf','dir'), mkdir('pdf'); end
for k = 1:numel(scripts)
    mlx = fullfile(pwd, 'mlx', [scripts{k} '.mlx']);
    matlab.internal.liveeditor.openAndSave(fullfile(pwd, [scripts{k} '.m']), mlx);
    matlab.internal.liveeditor.executeAndSave(mlx);
    export(mlx, fullfile(pwd, 'pdf', [scripts{k} '.pdf']));
    close all
    fprintf('>>> mlx %s\n', scripts{k});
end
end

function correr(nombre)
run(nombre);
end
