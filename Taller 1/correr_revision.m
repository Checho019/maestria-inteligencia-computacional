function correr_revision
% Corre la revision de datos (R1, R2) y los entrenamientos por paso (R3),
% y despues genera los tres live scripts ejecutados con su PDF.
% Es funcion porque los scripts empiezan con clear.
scripts = {'R1_revision_iris', 'R2_revision_banknote', 'R3_modelos_por_paso'};
for k = 1:numel(scripts)
    fprintf('\n######## %s ########\n', scripts{k});
    try
        correr(scripts{k});
        fprintf('>>> OK %s\n', scripts{k});
    catch e
        fprintf('>>> ERROR en %s: %s\n', scripts{k}, e.message);
        for j = 1:numel(e.stack)
            fprintf('    %s linea %d\n', e.stack(j).name, e.stack(j).line);
        end
    end
    close all
end
for k = 1:numel(scripts)
    mlx = fullfile(pwd, 'mlx', [scripts{k} '.mlx']);
    matlab.internal.liveeditor.openAndSave(fullfile(pwd, [scripts{k} '.m']), mlx);
    matlab.internal.liveeditor.executeAndSave(mlx);
    export(mlx, fullfile(pwd, 'pdf', [scripts{k} '.pdf']));
    close all
end
end

function correr(nombre)
run(nombre);
end
