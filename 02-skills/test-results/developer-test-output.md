# Factory Production System Architecture for Legion

## Executive Summary

You're asking the right question at the right time. A factory production system that scales to hundreds of machines while staying flexible for balance tuning is foundational work—get it right now, and you unlock emergent gameplay and designer agency. Get it wrong, and you'll rewrite it three times.

**The core answer: Decouple production logic into independent components, separate balance data from simulation, use event-driven communication, and batch update expensive operations.** This mirrors design systems thinking—your production rate token (a data value) must be completely separate from the component that consumes it (the implementation).

Let me walk through the WHY, the WHAT, and the HOW.

---

## Part 1: Architectural Philosophy

### Why This Matters for Your Design

Sean, you come from design systems. In design tokens, you learned that `--production-rate-factory-a: 10/sec` is a *value* that lives separately from the *implementation* (the C++ component that reads it). Games are the same.

**The trap:** Hardcoding production rates into machine classes. You ship with 50 machines, balance feels off, you recompile, re-ship. By 200 machines, your iteration loop is slow and error-prone.

**The solution:** Every tunable value lives in a DataTable. Every machine reads from that table at runtime. Designers change production_balance.csv in the Editor, hit reimport, and test live. No recompile. This is data-driven design.

### Scalability Constraints at 100+ Machines

At hundreds of machines, you hit three bottlenecks:

1. **CPU time per frame**: Each machine ticks, checks inputs, calculates output. 300 machines × 16ms frame time = you need ~50 microseconds per machine.
2. **Network/Save serialization**: Saving 300 machine states (position, health, inventory, production progress) becomes costly. You need to serialize only what's essential.
3. **Cache coherency**: Machines scattered across memory cause CPU cache misses. Batch-updating machines in tight loops is faster than ticking each individually.

**Our solution approach:**
- Use **component batching**: Separate production logic into a manager that ticks all ProductionComponents in a tight loop, not via Actor::Tick
- **Data layout**: Store machine state in dense arrays, not scattered actor properties
- **Async updates**: Heavy operations (conveyor flow, supply chain resolution) run on a separate thread or spread across frames

---

## Part 2: Core Architecture

### The Component Model: Composition Over Inheritance

Here's the machine hierarchy—and why it matters:

```
FactoryMachine (Actor)
├── TransformComponent          # Position, rotation (built-in)
├── StaticMeshComponent         # Visual (built-in)
├── ProductionComponent         # Produces resources (custom)
├── StorageComponent            # Holds inventory (custom)
├── PowerComponent              # Consumes/produces energy (custom)
├── HealthComponent             # Takes damage (custom)
└── ConveyorConnectionComponent # Routes to neighbors (custom)
```

**Why not inheritance?**
- Bad: `class FastFactory : public FactoryMachine { ProductionRate = 20.0f; }`
  - If you want a fast factory with low power, you're stuck with both changes. Mixing concerns.
  - A damaged factory that can't produce is awkward in the hierarchy.
- Good: Compose components. Each handles one concern.

**Why composition enables scaling:**
- You can swap ProductionComponent for a MiningComponent without touching the machine.
- You can add/remove PowerComponent dynamically (e.g., unpowering a machine to cool it down).
- Testing is easier: test ProductionComponent in isolation without the whole machine.
- Performance: All ProductionComponents can be ticked together by a manager.

### The Data-Driven Balance Layer

Create this structure in your Content folder:

```
Content/
├── Core/
│   └── Data/
│       ├── BuildingBalance.uasset      # DataTable with machine stats
│       ├── ProductionRecipes.uasset    # What each machine makes
│       └── GameConfig.json             # Economy, difficulty settings
```

**BuildingBalance DataTable** (the design token layer):

| Row Name | ProductionRate | Cost | PowerConsumption | HealthPoints | BuildTime |
|----------|---|---|---|---|---|
| Factory_Basic | 10.0 | 500 | 20 | 100 | 30 |
| Factory_Advanced | 25.0 | 1500 | 50 | 150 | 60 |
| Refinery_Copper | 8.0 | 800 | 30 | 100 | 40 |

Define the struct in C++:

```cpp
USTRUCT(BlueprintType)
struct FMachineBalanceRow : public FTableRowBase {
  UPROPERTY(EditAnywhere, BlueprintReadWrite)
  float ProductionRate = 10.f;  // Units per second

  UPROPERTY(EditAnywhere, BlueprintReadWrite)
  float Cost = 500.f;

  UPROPERTY(EditAnywhere, BlueprintReadWrite)
  float PowerConsumption = 20.f;

  UPROPERTY(EditAnywhere, BlueprintReadWrite)
  float HealthPoints = 100.f;

  UPROPERTY(EditAnywhere, BlueprintReadWrite)
  float BuildTime = 30.f;
};
```

**Why this matters:** A designer can tweak Factory_Basic's production rate to 12.0 in the Editor, reimport the DataTable, and test it live. No code recompile. No build step. This is the speed that lets you ship a balanced game.

### The Production Simulation Loop

Here's the core production component:

```cpp
UCLASS(ClassGroup=(Production), meta=(BlueprintSpawnableComponent))
class UProductionComponent : public UActorComponent {
public:
  // Configuration (loaded from DataTable)
  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Production")
  float ProductionRate = 10.f;  // Items per second

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Production")
  EResourceType InputResource = EResourceType::Iron;

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Production")
  EResourceType OutputResource = EResourceType::IronPlate;

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Production")
  float InputRequired = 1.f;  // How much input per output item

  // State
  UPROPERTY(BlueprintReadOnly, Category="Production")
  float AccumulatedOutput = 0.f;

  UPROPERTY(BlueprintReadOnly, Category="Production")
  bool bIsProducing = false;

  virtual void BeginPlay() override;
  virtual void TickComponent(float DeltaTime, ELevelTick TickType,
                             FActorComponentTickFunction* ThisTickFunction) override;

  // Events
  DECLARE_MULTICAST_DELEGATE_TwoParams(FOnItemProduced, EResourceType, float);
  FOnItemProduced OnItemProduced;

  DECLARE_MULTICAST_DELEGATE(FOnProductionStateChanged);
  FOnProductionStateChanged OnProductionStateChanged;

private:
  bool CanProduce() const;
  void ProduceItem();
};
```

The tick is simple and **deterministic**:

```cpp
void UProductionComponent::TickComponent(float DeltaTime, ELevelTick TickType,
                                         FActorComponentTickFunction* ThisTickFunction) {
  Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

  AFactoryMachine* Machine = Cast<AFactoryMachine>(GetOwner());
  if (!Machine) return;

  // Check if we can produce
  bool CanNow = CanProduce();
  if (CanNow != bIsProducing) {
    bIsProducing = CanNow;
    OnProductionStateChanged.Broadcast();
  }

  if (!bIsProducing) return;

  // Accumulate output over time
  AccumulatedOutput += ProductionRate * DeltaTime;

  // Emit complete items
  while (AccumulatedOutput >= 1.0f) {
    // Try to consume input
    float ConsumedInput = Machine->Storage->TryRemoveResource(InputResource, InputRequired);

    if (ConsumedInput >= InputRequired) {
      // Success: emit output
      OnItemProduced.Broadcast(OutputResource, 1.f);
      AccumulatedOutput -= 1.0f;
    } else {
      // Not enough input: revert and stop
      AccumulatedOutput = 0.f;
      break;
    }
  }
}

bool UProductionComponent::CanProduce() const {
  AFactoryMachine* Machine = Cast<AFactoryMachine>(GetOwner());
  if (!Machine) return false;

  // Check power
  if (Machine->Power->GetCurrentPower() < PowerRequired) return false;

  // Check if we have input space to consume from
  return Machine->Storage->GetAmount(InputResource) >= InputRequired;
}
```

**Key decisions:**
- **Accumulation pattern**: Instead of emitting one item per tick, we accumulate fractional production over time. This means a machine producing 10/sec will emit 1 item every 0.1 seconds, not clump all 10 at once.
- **Event broadcasting**: When production completes, we broadcast. Storage listens and updates inventory. UI listens and updates displays. If you want analytics, attach another listener—no code changes to Production.
- **Power check inside CanProduce**: If you lose power mid-production, the machine stops smoothly without data corruption.

---

## Part 3: The Storage & Conveyor System

### Storage Component: Inventory Management

```cpp
UCLASS(ClassGroup=(Storage), meta=(BlueprintSpawnableComponent))
class UStorageComponent : public UActorComponent {
public:
  virtual void BeginPlay() override;

  // Capacity config (from DataTable)
  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Storage")
  TMap<EResourceType, float> Capacity;  // Max per resource type

  // Current state
  UPROPERTY(BlueprintReadOnly, Category="Storage")
  TMap<EResourceType, float> Inventory;

  // Try to add resource; returns amount added
  UFUNCTION(BlueprintCallable, Category="Storage")
  float TryAddResource(EResourceType Type, float Amount);

  // Remove resource; returns amount removed
  UFUNCTION(BlueprintCallable, Category="Storage")
  float TryRemoveResource(EResourceType Type, float Amount);

  // Query
  UFUNCTION(BlueprintCallable, Category="Storage")
  float GetAmount(EResourceType Type) const;

  UFUNCTION(BlueprintCallable, Category="Storage")
  float GetCapacity(EResourceType Type) const;

  UFUNCTION(BlueprintCallable, Category="Storage")
  bool IsFull(EResourceType Type) const;

  // Events
  DECLARE_MULTICAST_DELEGATE_TwoParams(FOnInventoryChanged, EResourceType, float);
  FOnInventoryChanged OnInventoryChanged;

private:
  void ValidateInventory();
};

float UStorageComponent::TryAddResource(EResourceType Type, float Amount) {
  float Current = Inventory[Type];
  float Max = Capacity[Type];
  float AvailableSpace = Max - Current;

  float ToAdd = FMath::Min(Amount, AvailableSpace);
  Inventory[Type] += ToAdd;

  if (ToAdd > 0.f) {
    OnInventoryChanged.Broadcast(Type, Inventory[Type]);
  }

  return ToAdd;
}

float UStorageComponent::TryRemoveResource(EResourceType Type, float Amount) {
  float Current = Inventory[Type];
  float ToRemove = FMath::Min(Amount, Current);
  Inventory[Type] -= ToRemove;

  if (ToRemove > 0.f) {
    OnInventoryChanged.Broadcast(Type, Inventory[Type]);
  }

  return ToRemove;
}
```

### Conveyor Component: Routing Between Machines

Conveyors are the circulatory system. They pull from a source machine, push to a destination, and visualize flow.

```cpp
UCLASS(ClassGroup=(Conveyor), meta=(BlueprintSpawnableComponent))
class UConveyorComponent : public UActorComponent {
public:
  // Configuration
  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Conveyor")
  AFactoryMachine* SourceMachine = nullptr;

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Conveyor")
  AFactoryMachine* DestinationMachine = nullptr;

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Conveyor")
  EResourceType ResourceType = EResourceType::Iron;

  UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Conveyor")
  float TransferRate = 5.f;  // Items per second

  // State
  UPROPERTY(BlueprintReadOnly, Category="Conveyor")
  float CurrentFlow = 0.f;  // For animation feedback

  virtual void TickComponent(float DeltaTime, ELevelTick TickType,
                             FActorComponentTickFunction* ThisTickFunction) override;

  // Events
  DECLARE_MULTICAST_DELEGATE_OneParam(FOnFlowChanged, float);
  FOnFlowChanged OnFlowChanged;
};

void UConveyorComponent::TickComponent(float DeltaTime, ELevelTick TickType,
                                       FActorComponentTickFunction* ThisTickFunction) {
  Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

  if (!SourceMachine || !DestinationMachine) return;

  // Calculate how much to transfer this frame
  float AmountToTransfer = TransferRate * DeltaTime;

  // Pull from source
  float ActualRemoved = SourceMachine->Storage->TryRemoveResource(ResourceType, AmountToTransfer);

  // Push to destination
  float ActualAdded = DestinationMachine->Storage->TryAddResource(ResourceType, ActualRemoved);

  // If destination is full, return excess to source (logistics handles this)
  if (ActualAdded < ActualRemoved) {
    float ExcessAmount = ActualRemoved - ActualAdded;
    SourceMachine->Storage->TryAddResource(ResourceType, ExcessAmount);
  }

  // Track flow for animation
  CurrentFlow = ActualAdded;
  if (CurrentFlow != PreviousFlow) {
    OnFlowChanged.Broadcast(CurrentFlow);
    PreviousFlow = CurrentFlow;
  }
}
```

**Why conveyors as components:**
- Easy to add/remove at runtime. Drag a conveyor in the Editor, set source/dest, done.
- Flow feedback (animation) is decoupled from logic. The component broadcasts OnFlowChanged; a Material parameter listener updates material offset for the conveyor animation.
- Testing: Create two machines and a conveyor, verify flow. No world setup needed.

---

## Part 4: Scaling to 100+ Machines

### Problem 1: CPU Time Per Frame

At 300 machines ticking individually, you might spend 5-10ms per frame just in production updates. That's a frame budget problem.

**Solution: Batch Production Updates**

Create a factory manager that ticks all ProductionComponents in a tight loop:

```cpp
UCLASS()
class AFactoryManager : public AActor {
public:
  virtual void Tick(float DeltaTime) override;

  void RegisterMachine(AFactoryMachine* Machine);
  void UnregisterMachine(AFactoryMachine* Machine);

private:
  UPROPERTY()
  TArray<AFactoryMachine*> AllMachines;

  UPROPERTY()
  TArray<UProductionComponent*> ProductionComponents;

  // Batch update in tight loop
  void UpdateProduction(float DeltaTime);
};

void AFactoryManager::UpdateProduction(float DeltaTime) {
  // Tight loop: all production in cache-friendly memory access
  for (UProductionComponent* Prod : ProductionComponents) {
    if (!Prod->IsActive()) continue;

    // Manually tick component (bypassing Actor::Tick overhead)
    Prod->SimulateProduction(DeltaTime);
  }
}
```

**Why this matters:**
- Actor::Tick has overhead (bounds checks, component iteration, etc.). Batch updating skips that.
- All ProductionComponents iterated in sequence = better CPU cache hits.
- You can profile and optimize this loop without touching 300 individual actors.

### Problem 2: Save Serialization

Saving 300 machines × 10+ properties each is slow. You need **selective serialization**.

```cpp
USTRUCT(BlueprintType)
struct FMachineInstanceData {
  UPROPERTY()
  int32 MachineID;

  UPROPERTY()
  FString MachineType;  // "Factory_Basic", "Refinery_Copper", etc.

  UPROPERTY()
  FVector Location;

  UPROPERTY()
  float Health = 100.f;

  UPROPERTY()
  TMap<EResourceType, float> Inventory;

  // Don't save AccumulatedOutput—it's reset on load (okay to lose partial progress)
  // Don't save CurrentPower—recalculated on load
};

void AGameManager::SaveFactoryState() {
  TArray<FMachineInstanceData> SaveData;

  for (AFactoryMachine* Machine : AllMachines) {
    if (!Machine) continue;

    FMachineInstanceData Data;
    Data.MachineID = Machine->MachineID;
    Data.MachineType = Machine->MachineType;
    Data.Location = Machine->GetActorLocation();
    Data.Health = Machine->Health->GetCurrentHealth();
    Data.Inventory = Machine->Storage->GetInventory();

    SaveData.Add(Data);
  }

  // Serialize to disk
  UGameplayStatics::SaveGameToSlot(SaveData, FName("FactoryState"), 0);
}
```

**Key principle:** Don't save transient state. AccumulatedOutput resets on load. CurrentFlow is recalculated. This keeps save files small and load times fast.

### Problem 3: Supply Chain Logic

With 100+ machines, finding suppliers and routing resources becomes complex. Use a **supply request queue**:

```cpp
USTRUCT()
struct FSupplyRequest {
  EResourceType ResourceType;
  float Amount;
  AFactoryMachine* Requester;
  float Priority = 1.f;  // Higher = urgent
};

UCLASS()
class ASupplyChainManager : public AActor {
public:
  virtual void Tick(float DeltaTime) override;

  void RequestResource(AFactoryMachine* Requester, EResourceType Type, float Amount);

private:
  UPROPERTY()
  TArray<FSupplyRequest> PendingRequests;

  UPROPERTY()
  TArray<AFactoryMachine*> AllMachines;

  void ProcessRequests(float DeltaTime);
  AFactoryMachine* FindBestSupplier(EResourceType Type, float Amount);
};

void ASupplyChainManager::ProcessRequests(float DeltaTime) {
  // Sort by priority (urgent requests first)
  PendingRequests.Sort([](const FSupplyRequest& A, const FSupplyRequest& B) {
    return A.Priority > B.Priority;
  });

  for (FSupplyRequest& Req : PendingRequests) {
    AFactoryMachine* Supplier = FindBestSupplier(Req.ResourceType, Req.Amount);

    if (Supplier) {
      float Delivered = Supplier->Storage->TryRemoveResource(Req.ResourceType, Req.Amount);
      Req.Requester->Storage->TryAddResource(Req.ResourceType, Delivered);

      OnSupplyDelivered.Broadcast(Req.Requester, Req.ResourceType, Delivered);
    }
  }

  PendingRequests.Empty();
}
```

**Why this scales:**
- Decoupled from conveyors. Conveyors handle direct point-to-point flow; supply chain handles ad-hoc requests.
- Batch processing: All requests in one frame, not scattered across ticks.
- Async potential: Supply chain logic could run on a worker thread (with thread-safe queues).

---

## Part 5: Data-Driven Balance Workflow

This is where your design agency lives. Here's the workflow:

### Step 1: Designer Tunes in Editor

1. Open Content Browser → Data → BuildingBalance
2. Double-click to open DataTable
3. Edit Factory_Basic's ProductionRate from 10 to 12
4. Right-click → Reimport
5. Click Play in Editor
6. Observe: factories now produce 20% faster
7. Tweak more values, iterate freely

### Step 2: Load at Runtime

In your AFactoryMachine::BeginPlay():

```cpp
void AFactoryMachine::BeginPlay() {
  Super::BeginPlay();

  // Load balance data from DataTable
  UDataTable* BalanceTable = LoadObject<UDataTable>(
    nullptr,
    TEXT("/Game/Core/Data/BuildingBalance")
  );

  if (!BalanceTable) {
    UE_LOG(LogTemp, Error, TEXT("BuildingBalance not found!"));
    return;
  }

  FMachineBalanceRow* BalanceData = BalanceTable->FindRow<FMachineBalanceRow>(
    FName(*MachineType),  // e.g., "Factory_Basic"
    TEXT("LookupMachine")
  );

  if (BalanceData) {
    Production->ProductionRate = BalanceData->ProductionRate;
    Power->PowerConsumption = BalanceData->PowerConsumption;
    Health->MaxHealth = BalanceData->HealthPoints;
  }
}
```

### Step 3: Track What Changes

Every time you adjust a value, log it:

```cpp
void UAnalyticsManager::LogBalanceChange(FString MachineType, FString Property, float OldValue, float NewValue) {
  FAnalyticsEvent Event;
  Event.EventName = "balance_tuned";
  Event.Attributes.Add("machine_type", MachineType);
  Event.Attributes.Add("property", Property);
  Event.Attributes.Add("old_value", FString::Printf(TEXT("%.2f"), OldValue));
  Event.Attributes.Add("new_value", FString::Printf(TEXT("%.2f"), NewValue));
  SendEventToServer(Event);
}
```

Later, when you analyze playtests, you can correlate balance changes with player behavior. Did increasing Factory_Basic's cost to 600 make players explore more? Track it.

---

## Part 6: Event-Driven Integration

This is the "glue" that keeps systems decoupled.

### UI Listens to Production

```cpp
// In a UI widget for showing production status
void SProductionWidget::OnProductionBegin() {
  ProgressBar->SetValue(0.f);
  StatusText->SetText(FText::FromString("Producing..."));
}

void SProductionWidget::OnProductionStop() {
  StatusText->SetText(FText::FromString("Idle"));
}

void SProductionWidget::OnItemProduced(EResourceType Type, float Amount) {
  TotalProduced += Amount;
  ProductionCountText->SetText(FText::AsNumber(TotalProduced));
}

// In BeginPlay:
Production->OnProductionStateChanged.AddDynamic(this, &SProductionWidget::OnProductionBegin);
Production->OnItemProduced.AddDynamic(this, &SProductionWidget::OnItemProduced);
```

UI doesn't poll for state. Production pushes state via events. Result: UI is always in sync, no frame-delay.

### Analytics Listens to Everything

```cpp
class AAnalyticsListener {
public:
  void Initialize(AFactoryMachine* Machine) {
    Machine->Production->OnItemProduced.AddDynamic(
      this, &AAnalyticsListener::OnMachineProduced
    );
  }

  void OnMachineProduced(EResourceType Type, float Amount) {
    Analytics->LogResourceProduced(Type, Amount, Machine->MachineType);
  }
};
```

Add a listener to every machine in BeginPlay. Now you have per-machine production data for balance analysis.

---

## Part 7: Visual Feedback & Conveyors

Conveyors should visually communicate flow. Use **Material parameter animation**:

```cpp
void UConveyorComponent::OnFlowChanged_Implementation(float NewFlow) {
  // Material offset speed = flow * some scale
  float AnimSpeed = NewFlow / TransferRate;  // 0 to 1

  if (ConveyorMaterial) {
    ConveyorMaterial->SetScalarParameterValue(FName("ScrollSpeed"), AnimSpeed * 2.f);
  }
}
```

In your material, use a scrolling UV coordinate:

```
Texture2D Sample → UVs offset by Time * ScrollSpeed → into Base Color
```

Result: Faster flow = faster conveyor animation. Players instantly see when a production line is throttled.

---

## Part 8: Scalability Checklist

Before shipping, verify:

- [ ] **100 machines can run at 60 FPS** on target hardware. Profile with PIE (Play in Editor), monitor CPU time.
- [ ] **Save/load 100 machines in under 2 seconds** without freezing.
- [ ] **Conveyor flow updates every frame** with no stutters.
- [ ] **Designers can change production rates without recompiling.** Edit DataTable, reimport, play.
- [ ] **Supply chain requests don't deadlock.** If Machine A needs Iron from Machine B, and B needs Copper from A, the system doesn't hang.
- [ ] **UI updates are event-driven, not polling.** No `Tick()` calls in UI that read machine state.
- [ ] **Analytics captures per-machine metrics.** You can answer "which building type underperforms?"

---

## Part 9: Mod-Friendly Design

If you ever want community-created factories, design for extensibility:

### Modders Can Add Buildings via DataTable

1. Open BuildingBalance
2. Right-click → Add Row
3. Name it "CustomFactory_ModderName"
4. Fill in stats
5. Create a Blueprint child of BP_FactoryMachine, set MachineType to the new row name
6. Done. Custom factory exists.

### Modders Can Create New Resources

Extend the `EResourceType` enum (or use a string-based resource system for real mod support):

```cpp
// In a mod's Content:
// Create a DataAsset: CustomResources
// List: ["Titanium", "Plutonium", "Helium3"]
```

---

## Part 10: Performance Tuning Reference

### Profile Points

- **ProductionComponent::TickComponent**: Should be < 0.5ms for 300 machines
- **ConveyorComponent::TickComponent**: Should be < 0.3ms for 100 conveyors
- **SupplyChainManager::ProcessRequests**: Should be < 1ms (can run async)
- **Save serialization**: < 2 seconds for 300 machines

If any exceeds budget:
1. Batch update (remove individual Actor::Tick)
2. Async processing (move to worker thread or spread across frames)
3. Data layout (reorder memory access patterns for cache efficiency)

---

## Summary: The Architecture Blueprint

```
┌─────────────────────────────────────────────────────┐
│ Balance Layer (DataTables)                         │
│ - BuildingBalance.uasset (production rates, costs) │
│ - ProductionRecipes.uasset (input/output mixes)    │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ Machine Components (Logic)                         │
│ - ProductionComponent (produces resources)          │
│ - StorageComponent (holds inventory)                │
│ - PowerComponent (consumes/provides energy)         │
│ - ConveyorComponent (routes between machines)       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ Manager Systems (Coordination)                      │
│ - FactoryManager (batches production updates)       │
│ - SupplyChainManager (fulfills requests)            │
│ - GameManager (saves/loads state)                   │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ Event Bus (Loose Coupling)                         │
│ - OnItemProduced (flows to UI, Analytics, etc.)    │
│ - OnFlowChanged (animates conveyors)                │
│ - OnInventoryChanged (updates displays)             │
└─────────────────────────────────────────────────────┘
```

Every layer is independent. Change a balance value? Only the DataTable updates. Add UI feedback? Subscribe to events. Add analytics? New listener. No cascading code changes.

This is how you scale to hundreds of machines without rewriting the core system. This is how you ship a game that designers can tune without touching code. This is Legion's factory heartbeat.

---

## Questions for Further Work

1. **Multiplayer synchronization**: If machines tick on server, how do you sync state to clients efficiently?
2. **Undo/redo for building**: Should placing a machine have undo? That means tracking build state separately.
3. **Dynamic conveyor pathfinding**: Instead of fixed source/dest, could conveyors auto-route based on supply/demand?
4. **Mod content security**: How do you validate that a modded machine doesn't break economy balance?

These are future refinements. For now, this foundation gets you to 300 machines with designer agency and performance headroom.
