# 🦾 Bras Robotique — URDF / Xacro & MoveIt 2

> **Master 1 — Robotique & Systèmes embarqués**  
> TP Robotique Industrielle — K. Ramoth — 2026  
> Technologies : ROS 2 Humble · URDF/Xacro · MoveIt 2 · RViz 2

---

## 1. Présentation du robot et travail réalisé

Le robot modélisé est un **bras manipulateur à 4 degrés de liberté** avec une pince parallèle à deux doigts, de type bras hobby (similaire aux bras Arduino/servo). Il est composé de 7 liens rigides reliés par 6 joints.

### Chaîne cinématique

```
world (fixe)
  └─ base_link              ← socle fixe (mesh: basement.stl)
       └─ base_plate        ← joint1 : révolution Z — lacet ±180°
            └─ forward_drive_arm  ← joint2 : révolution Y — tangage ±90°
                 └─ horizontal_arm    ← joint3 : révolution Y — tangage ±90°
                      └─ claw_support      ← joint_claw : révolution Z — rotation ±90°
                           ├─ gripper_right  ← joint4 : prismatique (0 → 22 mm)
                           └─ gripper_left   ← joint5 : prismatique (mimic joint4 × −1)
```

### Travail réalisé

- Modélisation complète du bras en **Xacro** avec meshes STL, collisions simplifiées et inerties estimées
- Intégration dans **RViz 2** avec visualisation des TF et animation via `joint_state_publisher_gui`
- Génération du package **MoveIt 2** avec groupes cinématiques, SRDF, solveur KDL et planificateur OMPL



## 2. Justification du choix Xacro vs URDF pur

### ✅ Choix retenu : **Xacro modulaire**

| Critère | Justification |
|---|---|
| **Complexité** | 7 liens + 6 joints → plus de 300 lignes en URDF brut, difficile à maintenir |
| **Expressions mathématiques** | `${PI/2}` au lieu de `1.5707963` répété 12 fois dans le fichier |
| **Macros réutilisables** | Les deux doigts de la pince partagent la même structure d'inertie |
| **Maintenance** | Modifier l'échelle ou une masse globale se fait en un seul endroit |

**Avantages de Xacro :** expressions mathématiques natives, macros paramétriques, constantes nommées, possibilité d'inclure des fichiers séparés.

**Inconvénients :** nécessite `xacro` comme dépendance de build ; le URDF généré est moins lisible directement par un humain.

**Quand aurait-on choisi URDF pur ?** Pour un robot très simple (2–3 liens) ou pour compatibilité maximale avec des outils tiers ne supportant pas Xacro.

---

## 3. Hypothèses sur les inerties et limites articulaires

### Inerties

Les tenseurs d'inertie sont calculés analytiquement avec les formules des solides homogènes :
- Cylindre : `Ixx = Iyy = m(3r² + h²)/12`, `Izz = mr²/2`
- Pavé : `Ixx = m(y² + z²)/12`, etc.

### Limites articulaires

| Joint | Type | Plage | Effort max | Vitesse max |
|---|---|---|---|---|
| `joint1` | revolute | [−π, +π] | 50 N·m | 1.0 rad/s |
| `joint2` | revolute | [−π/2, +π/2] | 30 N·m | 1.0 rad/s |
| `joint3` | revolute | [−π/2, +π/2] | 30 N·m | 1.0 rad/s |
| `joint_claw` | revolute | [−π/2, +π/2] | 20 N·m | 1.0 rad/s |
| `joint4` | prismatic | [0, 0.022 m] | 10 N | 0.2 m/s |
| `joint5` | prismatic | mimic `joint4` × −1 | — | — |

---

## 4. Instructions d'installation pas-à-pas

### Prérequis système

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill (installé et sourcé)
- MoveIt 2

```bash
# Installer les dépendances ROS 2
sudo apt update
sudo apt install -y \
  ros-humble-moveit \
  ros-humble-xacro \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-robot-state-publisher \
  ros-humble-rviz2
```


### Compiler

```bash
cd ~/ros2_ws
colcon build 
```

### Sourcer l'environnement

```bash
source install/setup.bash

# Optionnel : ajouter au bashrc pour ne pas répéter
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

---

## 5. Commandes de lancement

### Visualisation RViz 2

```bash
ros2 launch robot_arm_description display.launch.py
```

Cela lance simultanément :
- **RViz 2** — visualisation 3D du robot avec les meshes
- **joint_state_publisher_gui** — fenêtre avec curseurs pour bouger chaque articulation
- **robot_state_publisher** — publication de la description et des TF

> Pour voir les **collisions** dans RViz : panneau gauche → `RobotModel` → `Visual Enabled: false` → `Collision Enabled: true`

> Pour vérifier l'arbre TF :
> ```bash
> ros2 run tf2_tools view_frames
> evince frames.pdf
> ```

### Démo MoveIt 2

```bash
ros2 launch robot_arm_moveit_config demo.launch.py
```

Dans RViz :
1. Sélectionner le groupe **arm** dans le panneau MoveIt
2. Déplacer la sphère interactive vers une pose cible
3. Cliquer **Plan** puis **Execute**

---

## 6. Captures d'écran

### RViz 2 — Modèle visuel (meshes STL)


![RViz model](docs/screenshots/rviz_model.png)

### RViz 2 — Représentation des collisions


![Collision shapes](docs/screenshots/rviz_collision.png)

*Géométries de collision simplifiées : cylindres pour le socle et la base_plate, boîtes pour les bras et la pince.*

### MoveIt 2 — Planification de trajectoire


![MoveIt planning](docs/screenshots/moveit_planning.png)

*Planification RRTConnect entre la pose `home` et une pose cible. La trajectoire est affichée en orange dans RViz.*

---

## 7. Difficultés rencontrées et solutions apportées

| # | Difficulté | Cause | Solution |
|---|---|---|---|
| 1 | **Erreur au lancement : `Unable to parse robot_description as yaml`** | ROS 2 Humble interprète le paramètre `robot_description` comme du YAML au lieu d'une chaîne | Entourer la valeur avec `ParameterValue(Command(['xacro ', xacro_file]), value_type=str)` dans le fichier launch |
| 2 | **Meshes invisibles ou géantes** | Les fichiers STL sont en unités millimètres mais ROS utilise des mètres | Application du `scale="0.01 0.01 0.01"` sur chaque balise `<mesh>` dans les visuels |
| 3 | **Orientations des meshes incorrectes** | Les meshes ne sont pas orientés dans le repère ROS par défaut | Utilisation des valeurs `rpy` exactes fournies dans le sujet pour chaque `<visual>` |
| 4 | **Robot figé dans RViz (joints fixes)** | La fenêtre `joint_state_publisher_gui` ne s'ouvrait pas automatiquement | Lancer manuellement `ros2 run joint_state_publisher_gui joint_state_publisher_gui` dans un second terminal |
| 5 | **`gripper_left` ne suivait pas `gripper_right`** | Le tag `<mimic>` absent du joint5 | Ajout de `<mimic joint="joint4" multiplier="-1"/>` dans la définition de `joint5` |
| 6 | **Fixed frame TF introuvable dans RViz** | Pas de lien `world` déclaré | Ajout d'un lien fictif `world` et d'un joint `world_fixed` de type `fixed` vers `base_link` |
| 7 | **Bras mal orienté / posture incorrecte** | Les axes de rotation des joints2 et joint3 étaient sur X au lieu de Y | Correction en `<axis xyz="0 1 0"/>` pour les joints de tangage du bras |
---

## Structure du dépôt

```
robot_arm_ros2/
├── robot_arm_description/          ← Package de description du robot
│   ├── urdf/
│   │   └── robot_arm.urdf.xacro   ← Fichier Xacro principal
│   ├── meshes/                     ← Fichiers STL (13 meshes)
│   │   ├── basement.stl
│   │   ├── base_plate.stl
│   │   ├── forward_drive_arm.stl
│   │   ├── horizontal_arm.stl
│   │   ├── claw_support.stl
│   │   ├── right_finger.stl
│   │   ├── left_finger.stl
│   │   └── ...
│   ├── launch/
│   │   └── display.launch.py       ← RViz 2 + joint_state_publisher_gui
│   ├── config/
│   │   └── robot_arm.rviz          ← Configuration RViz sauvegardée
│   ├── package.xml
│   └── CMakeLists.txt
├── robot_arm_moveit_config/        ← Package de configuration MoveIt 2
│   ├── config/
│   │   ├── robot_arm.srdf          ← Groupes cinématiques + collisions SRDF
│   │   ├── kinematics.yaml         ← Solveur KDL
│   │   ├── joint_limits.yaml       ← Limites articulaires MoveIt
│   │   ├── ompl_planning.yaml      ← Planificateur OMPL (RRTConnect par défaut)
│   │   └── moveit_controllers.yaml ← Contrôleurs simulés
│   ├── launch/
│   │   └── demo.launch.py          ← Démo MoveIt 2 + RViz 2
│   ├── package.xml
│   └── CMakeLists.txt
└── README.md
```

---


